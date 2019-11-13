import base64
import json
import time
import urllib

from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.httputil import url_concat
from traitlets import Integer

from . import utils


class RefreshUserMixin:
    """ The RefreshUserMixin is meant to be added to the GenericOAuthenticator to
    provide access_token renewal when it expires.
    """

    refresh_margin = Integer(
        5,
        allow_none=True,
        config=True,
        help=(
            "Number of seconds before expiry to trigger a renewal of the access "
            + "token. Set to None to use exact time."
        ),
    )

    async def refresh_user(self, user, handler=None):
        """Refresh auth data for a given user

        Use refresh token to obtain an new access token.
        Update identity info.

        Args:
            user (User): the user to refresh
            handler (tornado.web.RequestHandler or None): the current request handler
        Returns:
            auth_data (bool or dict):
                Return **True** if auth data for the user is up-to-date
                and no updates are required.

                Return **False** if the user's auth data has expired,
                and they should be required to login again.

                Return a **dict** of auth data if some values should be updated.
                This dict should have the same structure as that returned
                by :meth:`.authenticate()` when it returns a dict.
                Any fields present will refresh the value for the user.
                Any fields not present will be left unchanged.
                This can include updating `.admin` or `.auth_state` fields.
        """
        # Nothing to do if we don't have the auth state.
        if not self.enable_auth_state:
            raise "Refreshing user requires `enable_auth_state` to be set."

        auth_state = await user.get_auth_state()
        access_token = auth_state["access_token"]
        refresh_token = auth_state.get("refresh_token")
        refresh_access_token = refresh_token and not self._expired(refresh_token)

        if self._expired(access_token):
            if not refresh_access_token:
                return False
            try:
                new_auth_state = await self.idp_refresh_token(refresh_token)
            except Exception as e:
                self.log.warn(
                    "Failed to refresh access token for: %s, exception was %s",
                    user.name,
                    e,
                )
                return False

            if "refresh_token" in new_auth_state:
                auth_state["refresh_token"] = new_auth_state["refresh_token"]
            access_token = auth_state["access_token"] = new_auth_state["access_token"]

        try:
            userdata = await self.get_idp_userdata(access_token)
        except Exception as e:
            self.log.warn(
                "Failed to refresh auth info for: %s, exception was %s", user.name, e,
            )
            return False

        auth_state["oauth_user"] = userdata
        return {"auth_state": auth_state}

    def _expired(self, token):
        """Check whether a jwt token is expired or nearly so

        Check the token payload for the expiry date. If a margin is set with the
        `refresh_margin` option, it will return False by the amount of seconds in
        `refresh_margin` before it actually expires.

        Args:
            token (bytes): jwt token to verify

        Returns:
            expiry (bool):
               Return True if the token is expired, False otherwise.
        """
        payload = utils.get_payload(token)
        exp = int(payload.get("exp"))
        t = time.time() + (self.refresh_margin or 0)
        return exp <= t

    async def get_idp_userdata(self, access_token):
        """Refresh user info.

        Args:
           access_token (bytes): user's access token

        return user_info
        """
        headers = {
            "Accept": "application/json",
            "User-Agent": "JupyterHub",
            "Authorization": "Bearer {}".format(access_token),
        }

        url = url_concat(self.userdata_url, self.userdata_params)

        if self.userdata_token_method == "url":
            url = url_concat(self.userdata_url, dict(access_token=access_token))

        req = HTTPRequest(
            url,
            method=self.userdata_method,
            headers=headers,
            validate_cert=self.tls_verify,
        )
        resp = await AsyncHTTPClient().fetch(req)
        return json.loads(resp.body.decode("utf8", "replace"))

    async def idp_refresh_token(self, refresh_token):
        """Request a new access_token from the IdP.

        Use the refresh_token to obtain a new access token.

        Args:
           refresh_token (bytes): refresh_token
        """
        headers = {"Accept": "application/json", "User-Agent": "JupyterHub"}

        if self.basic_auth:
            b64key = base64.b64encode(
                bytes("{}:{}".format(self.client_id, self.client_secret), "utf8")
            )
            headers.update({"Authorization": "Basic {}".format(b64key.decode("utf8"))})

        params = dict(grant_type="refresh_token", refresh_token="refresh_token")

        req = HTTPRequest(
            self.token_url,
            method="POST",
            headers=headers,
            validate_cert=self.tls_verify,
            body=urllib.parse.urlencode(params),
        )
        resp = await AsyncHTTPClient().fetch(req)
        return json.loads(resp.body.decode("utf8", "replace"))
