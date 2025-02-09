from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rorapp.models import Faction
from rorapp.game_state.send_game_state import send_game_state


@receiver(post_save, sender=Faction)
def faction_created(sender, instance, created, **kwargs):
    if created:
        if instance.game:
            game_id = instance.game.id
            send_game_state(game_id)


@receiver(post_delete, sender=Faction)
def faction_deleted(sender, instance, **kwargs):
    if instance.game:
        game_id = instance.game.id
        send_game_state(game_id)
