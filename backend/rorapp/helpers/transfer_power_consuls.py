from rorapp.models import Game, Log, Senator


def transfer_power_consuls(
    game_id: int, rome_consul_id: int, field_consul_id: int
) -> bool:
    game = Game.objects.get(id=game_id)
    senators = Senator.objects.filter(game=game_id, alive=True)

    # Clear existing offices
    for s in senators:
        if s.has_title(Senator.Title.ROME_CONSUL) or s.has_title(
            Senator.Title.FIELD_CONSUL
        ):
            s.add_title(Senator.Title.PRIOR_CONSUL)

        s.remove_title(Senator.Title.ROME_CONSUL)
        s.remove_title(Senator.Title.FIELD_CONSUL)
        s.remove_title(Senator.Title.HRAO)
        s.remove_title(Senator.Title.PRESIDING_MAGISTRATE)
        s.save()

    # Set Rome Consul
    rome_consul = senators.get(id=rome_consul_id)
    rome_consul.remove_status_item(Senator.StatusItem.INCOMING_CONSUL)
    rome_consul.remove_status_item(Senator.StatusItem.PREFERS_ROME_CONSUL)
    rome_consul.remove_status_item(Senator.StatusItem.PREFERS_FIELD_CONSUL)
    rome_consul.add_title(Senator.Title.ROME_CONSUL)
    rome_consul.add_title(Senator.Title.HRAO)
    rome_consul.add_title(Senator.Title.PRESIDING_MAGISTRATE)
    rome_consul.influence += 5
    rome_consul.save()

    # Set Field Consul
    field_consul = senators.get(id=field_consul_id)
    field_consul.remove_status_item(Senator.StatusItem.INCOMING_CONSUL)
    field_consul.remove_status_item(Senator.StatusItem.PREFERS_ROME_CONSUL)
    field_consul.remove_status_item(Senator.StatusItem.PREFERS_FIELD_CONSUL)
    field_consul.add_title(Senator.Title.FIELD_CONSUL)
    field_consul.influence += 5
    field_consul.save()

    # Log
    if not rome_consul.faction:
        return False
    Log.create_object(
        game_id,
        f"{rome_consul.display_name} of {rome_consul.faction.display_name} took over as presiding magistrate and Rome Consul. Both consuls gained 5 influence.",
    )

    # Progress game
    game.phase = Game.Phase.SENATE
    game.sub_phase = Game.SubPhase.OTHER_BUSINESS
    game.save()
    return True
