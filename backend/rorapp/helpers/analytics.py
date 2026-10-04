from datetime import datetime, timezone, timedelta

import posthog
from django.conf import settings


def capture_user_active(request) -> None:
    if not settings.POSTHOG_API_KEY:
        return
    now = datetime.now(timezone.utc)
    last_active = request.session.get("last_active_time")
    if not last_active or now - datetime.fromisoformat(last_active) > timedelta(hours=1):
        posthog.capture(str(request.user.id), "user_active")
        request.session["last_active_time"] = now.isoformat()
