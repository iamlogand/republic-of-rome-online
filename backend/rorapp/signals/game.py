from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rorapp.models import Game
from rorapp.game_state.send_game_state import send_game_state


@receiver(post_save, sender=Game)
def game_created(sender, instance, created, **kwargs):
    if created:
        send_game_state(instance.id)


@receiver(post_delete, sender=Game)
def game_updated(sender, instance, **kwargs):
    send_game_state(instance.id)
