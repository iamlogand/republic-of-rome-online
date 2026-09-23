import os
from django.http import JsonResponse
from dotenv import load_dotenv
from pathlib import Path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))
discord_invite_url = os.getenv("DISCORD_INVITE_URL")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_discord_invite_url(request):
    return JsonResponse({"discord_invite_url": discord_invite_url}, status=200)
