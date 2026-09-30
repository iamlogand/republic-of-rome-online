import posthog
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

posthog.project_api_key = settings.POSTHOG_API_KEY
posthog.host = "https://eu.i.posthog.com"


@receiver(post_save, sender=User)
def on_user_registered(sender, instance, created, **kwargs):
    if created and settings.POSTHOG_API_KEY:
        posthog.capture(str(instance.id), "user_registered")
