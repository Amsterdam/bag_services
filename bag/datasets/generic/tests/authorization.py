import time
import jwt

from django.conf import settings

from authorization_django import levels as authorization_levels


class AuthorizationSetup(object):
    """
    Helper methods to setup JWT tokens and authorization levels

    sets the following attributes:

    token_default
    token_employee
    token_employee_plus
    """

    def setUpAuthorization(self):
        """
        SET

        token_default
        token_employee
        token_employee_plus

        to use with:

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee_plus))

        """
        # NEW STYLE AUTH
        key = settings.DATAPUNT_AUTHZ['JWT_SECRET_KEY']
        algorithm = settings.DATAPUNT_AUTHZ['JWT_ALGORITHM']

        now = int(time.time())

        token_default = jwt.encode({
            'authz': authorization_levels.LEVEL_DEFAULT,
            'iat': now, 'exp': now + 600}, key, algorithm=algorithm)
        token_employee = jwt.encode({
            'authz': authorization_levels.LEVEL_EMPLOYEE,
            'iat': now, 'exp': now + 600}, key, algorithm=algorithm)
        token_employee_plus = jwt.encode({
            'authz': authorization_levels.LEVEL_EMPLOYEE_PLUS,
            'iat': now, 'exp': now + 600}, key, algorithm=algorithm)
        token_scope_brk_rs = jwt.encode({
            'scopes': [authorization_levels.SCOPE_BRK_RS],
            'iat': now, 'exp': now + 600}, key, algorithm=algorithm)
        token_scope_brk_rsn = jwt.encode({
            'scopes': [authorization_levels.SCOPE_BRK_RSN, authorization_levels.SCOPE_BRK_RS],
            'iat': now, 'exp': now + 600}, key, algorithm=algorithm)
        token_scope_brk_rzr = jwt.encode({
            'scopes': [authorization_levels.SCOPE_BRK_RZR],
            'iat': now, 'exp': now + 600}, key, algorithm=algorithm)
        token_scope_wkpd_rdbu = jwt.encode({
            'scopes': [authorization_levels.SCOPE_WKPB_RBDU],
            'iat': now, 'exp': now + 600}, key, algorithm=algorithm)


        self.token_default = str(token_default, 'utf-8')
        self.token_employee = str(token_employee, 'utf-8')
        self.token_employee_plus = str(token_employee_plus, 'utf-8')
        self.token_scope_brk_rs = str(token_scope_brk_rs, 'utf-8')
        self.token_scope_brk_rsn = str(token_scope_brk_rsn, 'utf-8')
        self.token_scope_brk_rzr = str(token_scope_brk_rzr, 'utf-8')
        self.token_scope_wkpd_rdbu = str(token_scope_wkpd_rdbu, 'utf-8')

