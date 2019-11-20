from oauthenticator.generic import GenericOAuthenticator
from .refresh_user_mixin import RefreshUserMixin


class ClbAuthenticator(RefreshUserMixin, GenericOAuthenticator):
    """ Collaboratory authenticator based on generic authenticator."""
    refresh_pre_spawn = True
    auth_refresh_age = 900
    enable_auth_state = True
