# Generated by Django 4.2.2 on 2023-09-02 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0028_notification_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='faction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rorapp.faction'),
        ),
    ]
