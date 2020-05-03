from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header


class UserAuthentication(TokenAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            return None
        try:
            token = auth[0].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)
