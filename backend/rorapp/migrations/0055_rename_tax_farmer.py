# Generated by Django 4.2.3 on 2024-03-02 19:14

from django.db import migrations


def get_new_name(tax_farmer_number: str):
    match tax_farmer_number:
        case "1":
            return "Latium"
        case "2":
            return "Etruria"
        case "3":
            return "Samnium"
        case "4":
            return "Campania"
        case "5":
            return "Apulia"
        case "6":
            return "Lucania"


class Migration(migrations.Migration):
    def rename_tax_farmer_situations_and_secrets(apps, schema_editor):
        Situation = apps.get_model("rorapp", "Situation")
        Secret = apps.get_model("rorapp", "Secret")
        for situation in Situation.objects.filter(
            type="concession", name__startswith="Tax Farmer"
        ):
            situation.name = get_new_name(situation.name[-1]) + " Tax Farmer"
            situation.save()
        for secret in Secret.objects.filter(
            type="concession", name__startswith="Tax Farmer"
        ):
            secret.name = get_new_name(secret.name[-1]) + " Tax Farmer"
            secret.save()

    dependencies = [
        ("rorapp", "0054_alter_enemyleader_dead_alter_senator_alive"),
    ]

    operations = [
        migrations.RunPython(
            rename_tax_farmer_situations_and_secrets,  # type: ignore
            migrations.RunPython.noop,
        ),
    ]
