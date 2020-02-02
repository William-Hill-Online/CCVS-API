from core.jwt.authentication import authenticate
from rest_framework.permissions import BasePermission


class JWTAPIPermission(BasePermission):
    """Returns whether the scope is inside the JWT payload."""

    def has_permission(self, request, view):
        jwt_payload = authenticate(request)
        method = view.required_scopes.get(request.method.upper())
        if method:
            payload_scopes = jwt_payload['scope'].split(' ') if jwt_payload else []
            result = all(elem in payload_scopes for elem in method)
            return result

        return True
