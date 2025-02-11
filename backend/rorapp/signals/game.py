from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rorapp.models import Game
from rorapp.game_state.send_game_state import send_game_state


@receiver(post_save, sender=Game)
@receiver(post_delete, sender=Game)
def game_updated(sender, instance, **kwargs):
    game_id = instance.id

    # TODO: Consider calling send_game_state from somewhere else because this might be getting called too often
    send_game_state(game_id)
