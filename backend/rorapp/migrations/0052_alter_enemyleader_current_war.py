# Generated by Django 4.2.3 on 2024-02-24 16:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0051_remove_war_matching_wars'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enemyleader',
            name='current_war',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rorapp.war'),
        ),
    ]
