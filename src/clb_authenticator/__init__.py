import time

from oauthenticator.generic import GenericOAuthenticator
from .refresh_user_mixin import RefreshUserMixin


class ClbAuthenticator(GenericOAuthenticator, RefreshUserMixin):
    """ Collaboratory authenticator based on generic authenticator."""
    refresh_pre_spawn = True
    enable_auth_state = True
