import time

from jwcrypto.jwt import JWT
from authorization_django.jwks import get_keyset

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
        jwks = get_keyset()
        assert len(jwks['keys']) > 0

        key = next(iter(jwks['keys']))
        now = int(time.time())

        header = {
            'alg': 'ES256',  # algorithm of the test key
            'kid': key.key_id
        }

        token_default = JWT(
            header=header,
            claims={
                'iat': now, 'exp': now + 600, 'scopes': []
            }
        )
        token_employee_plus = JWT(
            header=header,
            claims={
                'iat': now, 'exp': now + 600,
                'scopes': [
                    authorization_levels.SCOPE_BRK_RSN,
                    authorization_levels.SCOPE_BRK_RS,
                    authorization_levels.SCOPE_BRK_RO,
                    authorization_levels.SCOPE_WKPB_RBDU
                ]
            }
        )
        token_scope_brk_rs = JWT(
            header=header,
            claims={
                'iat': now, 'exp': now + 600,
                'scopes': [authorization_levels.SCOPE_BRK_RS]
            }
        )
        token_scope_brk_rsn = JWT(
            header=header,
            claims={
                'iat': now, 'exp': now + 600,
                'scopes': [
                    authorization_levels.SCOPE_BRK_RSN,
                    authorization_levels.SCOPE_BRK_RS
                ]
            }
        )
        token_scope_brk_ro = JWT(
            header=header,
            claims={
                'iat': now, 'exp': now + 600,
                'scopes': [authorization_levels.SCOPE_BRK_RO]
            }
        )
        token_scope_wkpd_rdbu = JWT(
            header=header,
            claims={
                'iat': now, 'exp': now + 600,
                'scopes': [authorization_levels.SCOPE_WKPB_RBDU]
            }
        )

        token_default.make_signed_token(key)
        self.token_default = token_default.serialize()

        token_employee_plus.make_signed_token(key)
        self.token_employee_plus = token_employee_plus.serialize()

        token_scope_brk_rs.make_signed_token(key)
        self.token_scope_brk_rs = token_scope_brk_rs.serialize()

        token_scope_brk_rsn.make_signed_token(key)
        self.token_scope_brk_rsn = token_scope_brk_rsn.serialize()

        token_scope_brk_ro.make_signed_token(key)
        self.token_scope_brk_ro = token_scope_brk_ro.serialize()

        token_scope_wkpd_rdbu.make_signed_token(key)
        self.token_scope_wkpd_rdbu = token_scope_wkpd_rdbu.serialize()
