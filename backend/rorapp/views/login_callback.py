import os
from django.http import HttpResponse
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))
frontend_origin = os.getenv("FRONTEND_ORIGINS", "").split(",")[0]
debug_mode = os.getenv("DEBUG") == "True"


def login_callback(request):
    """
    Redirect to frontend auth callback, passing session as a cookie.
    """

    session_id = request.session.session_key
    redirect_url = f"{frontend_origin}/auth/callback"

    response = HttpResponse(status=302)
    response["Location"] = redirect_url
    response.set_cookie(
        "sessionid",
        session_id,
        httponly=True,
        secure=not(debug_mode),
        samesite="Strict",
    )
    return response
