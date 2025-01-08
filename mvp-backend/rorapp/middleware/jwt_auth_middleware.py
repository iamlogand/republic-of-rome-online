from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from jwt import decode as jwt_decode
from django.contrib.auth.models import User, AnonymousUser
from django.conf import settings
from urllib.parse import parse_qs


@database_sync_to_async
def get_user(token):
    # Check if token is empty
    if not token.strip():
        return AnonymousUser()

    # This will automatically validate the token and raise an error if token is invalid
    UntypedToken(token)
    decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    return User.objects.get(id=decoded_data["user_id"])


class JwtAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Get the token
        query_string = parse_qs(scope["query_string"].decode("utf8"))
        if "token" in query_string:
            token = query_string["token"][0]
            user = await get_user(token)
            scope["user"] = user
        else:
            # If no token is provided, set user as AnonymousUser
            scope["user"] = AnonymousUser()
        return await self.app(scope, receive, send)
