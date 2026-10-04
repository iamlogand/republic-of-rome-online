import os
from datetime import date
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from dotenv import load_dotenv
from pathlib import Path
import posthog


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))
debug_mode = os.getenv("DEBUG") == "True"
parent_domain = os.getenv("PARENT_DOMAIN")


@ensure_csrf_cookie
def auth_status(request):
    """
    This view sets a CSRF cookie and returns it in the response.
    """

    csrf_token = request.META.get("CSRF_COOKIE", "")

    data = {"csrftoken": csrf_token}
    if request.user.is_authenticated:
        data["id"] = request.user.id
        data["username"] = request.user.username
        data["first_name"] = request.user.first_name
        data["last_name"] = request.user.last_name
        data["email"] = request.user.email

        today = str(date.today())
        if settings.POSTHOG_API_KEY and request.session.get("last_active_date") != today:
            posthog.capture(str(request.user.id), "user_active")
            request.session["last_active_date"] = today

    response = JsonResponse(data, status=200)
    response.set_cookie(
        "csrftoken",
        csrf_token,
        httponly=False,
        secure=not(debug_mode),
        samesite="Lax",
        domain=parent_domain
    )
    return response
