import django.db.models
from django.db import migrations


# Mappings from old values to new values

PHASE_MAP = {
    "Initial": "initial",
    "Mortality": "mortality",
    "Revenue": "revenue",
    "Forum": "forum",
    "Population": "population",
    "Senate": "senate",
    "Combat": "combat",
    "Revolution": "revolution",
}

SUB_PHASE_MAP = {
    "Attract knight": "attract knight",
    "Consular election": "consular election",
    "End": "end",
    "Faction leader": "faction leader",
    "Initiative auction": "initiative auction",
    "Initiative roll": "initiative roll",
    "Other business": "other business",
    "Redistribution": "redistribution",
    "Resolution": "resolution",
    "Sponsor games": "sponsor games",
    "Start": "start",
    "Play statesmen/concessions": "play statesmen/concessions",
}

SENATOR_STATUS_ITEM_MAP = {
    "Abstained": "abstained",
    "Contributed": "contributed",
    "Consent required": "consent required",
    "Voted nay": "voted nay",
    "Voted yea": "voted yea",
    "Incoming consul": "incoming consul",
    "Prefers Field Consul": "prefers Field Consul",
    "Prefers Rome Consul": "prefers Rome Consul",
    "Preferred attacker": "preferred attacker",
}

SENATOR_TITLE_MAP = {
    "Faction leader": "faction leader",
    "Presiding magistrate": "presiding magistrate",
    "Prior consul": "prior consul",
    "Proconsul": "proconsul",
}

FACTION_STATUS_ITEM_MAP = {
    "Auction winner": "auction winner",
    "Done": "done",
    "Current bidder": "current bidder",
    "Current initiative": "current initiative",
    "Skipped": "skipped",
    "Called to vote": "called to vote",
    "Awaiting decision": "awaiting decision",
}

WAR_STATUS_MAP = {
    "Inactive": "inactive",
    "Imminent": "imminent",
    "Active": "active",
}

CONCESSION_MAP = {
    "Harbor Fees": "harbor fees",
    "Mining": "mining",
    "Latium Tax Farmer": "Latium tax farmer",
    "Etruria Tax Farmer": "Etruria tax farmer",
    "Samnium Tax Farmer": "Samnium tax farmer",
    "Campania Tax Farmer": "Campania tax farmer",
    "Apulia Tax Farmer": "Apulia tax farmer",
    "Lucania Tax Farmer": "Lucania tax farmer",
}


def map_json_list(items, mapping):
    """Map old values to new values in a JSON list, handling dynamic prefixes too."""
    new_items = []
    for item in items:
        if item in mapping:
            new_items.append(mapping[item])
        elif item.startswith("Bid "):
            new_items.append("bid " + item[4:])
        elif item.startswith("Initiative "):
            new_items.append("initiative " + item[11:])
        else:
            new_items.append(item)
    return new_items


def forwards(apps, schema_editor):
    Game = apps.get_model("rorapp", "Game")
    Senator = apps.get_model("rorapp", "Senator")
    Faction = apps.get_model("rorapp", "Faction")
    Log = apps.get_model("rorapp", "Log")

    War = apps.get_model("rorapp", "War")

    # Update Game phase and sub_phase
    for old, new in PHASE_MAP.items():
        Game.objects.filter(phase=old).update(phase=new)
        Log.objects.filter(phase=old).update(phase=new)
    for old, new in SUB_PHASE_MAP.items():
        Game.objects.filter(sub_phase=old).update(sub_phase=new)

    # Update War status
    for old, new in WAR_STATUS_MAP.items():
        War.objects.filter(status=old).update(status=new)

    # Update Game concessions (JSONField)
    for game in Game.objects.all():
        new_concessions = map_json_list(game.concessions, CONCESSION_MAP)
        if new_concessions != game.concessions:
            game.concessions = new_concessions
            game.save(update_fields=["concessions"])

    # Update Senator status_items, titles, and concessions (all JSONFields)
    for senator in Senator.objects.all():
        changed = False
        new_status = map_json_list(senator.status_items, SENATOR_STATUS_ITEM_MAP)
        if new_status != senator.status_items:
            senator.status_items = new_status
            changed = True
        new_titles = map_json_list(senator.titles, SENATOR_TITLE_MAP)
        if new_titles != senator.titles:
            senator.titles = new_titles
            changed = True
        new_concessions = map_json_list(senator.concessions, CONCESSION_MAP)
        if new_concessions != senator.concessions:
            senator.concessions = new_concessions
            changed = True
        if changed:
            senator.save(update_fields=["status_items", "titles", "concessions"])

    # Update Faction status_items (JSONField)
    for faction in Faction.objects.all():
        new_status = map_json_list(faction.status_items, FACTION_STATUS_ITEM_MAP)
        if new_status != faction.status_items:
            faction.status_items = new_status
            faction.save(update_fields=["status_items"])


def backwards(apps, schema_editor):
    Game = apps.get_model("rorapp", "Game")
    Senator = apps.get_model("rorapp", "Senator")
    Faction = apps.get_model("rorapp", "Faction")

    Log = apps.get_model("rorapp", "Log")
    War = apps.get_model("rorapp", "War")

    reverse_phase = {v: k for k, v in PHASE_MAP.items()}
    reverse_sub_phase = {v: k for k, v in SUB_PHASE_MAP.items()}
    reverse_war_status = {v: k for k, v in WAR_STATUS_MAP.items()}
    reverse_senator_status = {v: k for k, v in SENATOR_STATUS_ITEM_MAP.items()}
    reverse_senator_title = {v: k for k, v in SENATOR_TITLE_MAP.items()}
    reverse_faction_status = {v: k for k, v in FACTION_STATUS_ITEM_MAP.items()}
    reverse_concession = {v: k for k, v in CONCESSION_MAP.items()}

    def reverse_json_list(items, mapping):
        new_items = []
        for item in items:
            if item in mapping:
                new_items.append(mapping[item])
            elif item.startswith("bid "):
                new_items.append("Bid " + item[4:])
            elif item.startswith("initiative "):
                new_items.append("Initiative " + item[11:])
            else:
                new_items.append(item)
        return new_items

    for old, new in reverse_phase.items():
        Game.objects.filter(phase=old).update(phase=new)
        Log.objects.filter(phase=old).update(phase=new)
    for old, new in reverse_sub_phase.items():
        Game.objects.filter(sub_phase=old).update(sub_phase=new)

    for old, new in reverse_war_status.items():
        War.objects.filter(status=old).update(status=new)

    for game in Game.objects.all():
        new_concessions = reverse_json_list(game.concessions, reverse_concession)
        if new_concessions != game.concessions:
            game.concessions = new_concessions
            game.save(update_fields=["concessions"])

    for senator in Senator.objects.all():
        changed = False
        new_status = reverse_json_list(senator.status_items, reverse_senator_status)
        if new_status != senator.status_items:
            senator.status_items = new_status
            changed = True
        new_titles = reverse_json_list(senator.titles, reverse_senator_title)
        if new_titles != senator.titles:
            senator.titles = new_titles
            changed = True
        new_concessions = reverse_json_list(senator.concessions, reverse_concession)
        if new_concessions != senator.concessions:
            senator.concessions = new_concessions
            changed = True
        if changed:
            senator.save(update_fields=["status_items", "titles", "concessions"])

    for faction in Faction.objects.all():
        new_status = reverse_json_list(faction.status_items, reverse_faction_status)
        if new_status != faction.status_items:
            faction.status_items = new_status
            faction.save(update_fields=["status_items"])


class Migration(migrations.Migration):

    dependencies = [
        ("rorapp", "0041_game_concessions_senator_concessions_and_more"),
    ]

    operations = [
        # AlterField for phase/sub_phase to update TextChoices definitions
        # Run data migration first to update existing values
        migrations.RunPython(forwards, backwards),
        # AlterField for phase/sub_phase to update TextChoices definitions
        migrations.AlterField(
            model_name="game",
            name="phase",
            field=django.db.models.CharField(
                blank=True,
                choices=[
                    ("initial", "initial"),
                    ("mortality", "mortality"),
                    ("revenue", "revenue"),
                    ("forum", "forum"),
                    ("population", "population"),
                    ("senate", "senate"),
                    ("combat", "combat"),
                    ("revolution", "revolution"),
                ],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="log",
            name="phase",
            field=django.db.models.CharField(
                blank=True,
                choices=[
                    ("initial", "initial"),
                    ("mortality", "mortality"),
                    ("revenue", "revenue"),
                    ("forum", "forum"),
                    ("population", "population"),
                    ("senate", "senate"),
                    ("combat", "combat"),
                    ("revolution", "revolution"),
                ],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="war",
            name="status",
            field=django.db.models.CharField(
                choices=[
                    ("inactive", "inactive"),
                    ("imminent", "imminent"),
                    ("active", "active"),
                ],
                max_length=12,
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="sub_phase",
            field=django.db.models.CharField(
                blank=True,
                choices=[
                    ("attract knight", "attract knight"),
                    ("consular election", "consular election"),
                    ("end", "end"),
                    ("faction leader", "faction leader"),
                    ("initiative auction", "initiative auction"),
                    ("initiative roll", "initiative roll"),
                    ("other business", "other business"),
                    ("redistribution", "redistribution"),
                    ("resolution", "resolution"),
                    ("sponsor games", "sponsor games"),
                    ("start", "start"),
                    ("play statesmen/concessions", "play statesmen/concessions"),
                ],
                max_length=30,
                null=True,
            ),
        ),
    ]
