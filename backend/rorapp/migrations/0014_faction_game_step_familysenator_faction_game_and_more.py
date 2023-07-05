# Generated by Django 4.2.2 on 2023-07-05 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0013_alter_waitlistentry_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Faction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='step',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='FamilySenator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('faction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='rorapp.faction')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rorapp.game')),
            ],
        ),
        migrations.AddField(
            model_name='faction',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rorapp.game'),
        ),
        migrations.AddField(
            model_name='faction',
            name='player',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='rorapp.gameparticipant'),
        ),
    ]
