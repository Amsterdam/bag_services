import time
import jwt

from authorization_django.config import settings as middleware_settings

from bag import authorization_levels


class AuthorizationSetup(object):
    """
    Helper methods to setup JWT tokens and authorization scopes

    sets the following attributes:

    token_default
    token_employee_plus
    token_scope_brk_rs
    token_scope_brk_rsn
    token_scope_brk_ro
    token_scope_wkpd_rdbu

    """

    def setUpAuthorization(self):
        """
        SET

        token_default
        token_employee_plus
        token_scope_brk_rs
        token_scope_brk_rsn
        token_scope_brk_ro
        token_scope_wkpd_rdbu

        to use with:

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee_plus))

        """
        # VERY NEW STYLE AUTH
        # Use JWKS defined in settings
        jwks = middleware_settings()['JWKS'].signers
        assert len(jwks) > 0
        (kid, key), = jwks.items()

        now = int(time.time())

        token_default = jwt.encode({
            'scopes': [],
            'iat': now, 'exp': now + 600}, key.key, algorithm=key.alg, headers={'kid': kid})
        token_employee_plus = jwt.encode({
            'scopes': [
                authorization_levels.SCOPE_BRK_RSN, authorization_levels.SCOPE_BRK_RS,
                authorization_levels.SCOPE_BRK_RO, authorization_levels.SCOPE_WKPB_RBDU],
            'iat': now, 'exp': now + 600}, key.key, algorithm=key.alg, headers={'kid': kid})
        token_scope_brk_rs = jwt.encode({
            'scopes': [authorization_levels.SCOPE_BRK_RS],
            'iat': now, 'exp': now + 600}, key.key, algorithm=key.alg, headers={'kid': kid})
        token_scope_brk_rsn = jwt.encode({
            'scopes': [authorization_levels.SCOPE_BRK_RSN, authorization_levels.SCOPE_BRK_RS],
            'iat': now, 'exp': now + 600}, key.key, algorithm=key.alg, headers={'kid': kid})
        token_scope_brk_ro = jwt.encode({
            'scopes': [authorization_levels.SCOPE_BRK_RO],
            'iat': now, 'exp': now + 600}, key.key, algorithm=key.alg, headers={'kid': kid})
        token_scope_wkpd_rdbu = jwt.encode({
            'scopes': [authorization_levels.SCOPE_WKPB_RBDU],
            'iat': now, 'exp': now + 600}, key.key, algorithm=key.alg, headers={'kid': kid})

        self.token_default = str(token_default, 'utf-8')
        self.token_employee_plus = str(token_employee_plus, 'utf-8')
        self.token_scope_brk_rs = str(token_scope_brk_rs, 'utf-8')
        self.token_scope_brk_rsn = str(token_scope_brk_rsn, 'utf-8')
        self.token_scope_brk_ro = str(token_scope_brk_ro, 'utf-8')
        self.token_scope_wkpd_rdbu = str(token_scope_wkpd_rdbu, 'utf-8')
