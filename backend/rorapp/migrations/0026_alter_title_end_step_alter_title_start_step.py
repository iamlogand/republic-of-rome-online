# Generated by Django 4.2.2 on 2023-08-31 06:36
# Edited by Logan on 2023-08-31: added the update_title_steps operation

from django.db import migrations, models
import django.db.models.deletion


# Update titles to use the IDs of the corresponding Steps for start_step and end_step
# instead of the indexes of the corresponding Steps, which didn't even match up anyway
def update_title_steps(apps, schema_editor):
    Title = apps.get_model('rorapp', 'Title')
    Step = apps.get_model('rorapp', 'Step')
    
    # Loop over all titles
    for title in Title.objects.all():

        # Get the game
        game = title.senator.game
        
        print('game:', game)
        print('title.start_step:', title.start_step)
        print('step objects:', Step.objects.filter(phase__turn__game=game))

        # Update the start_step and end_step fields with the IDs of the corresponding Steps
        title.start_step = Step.objects.get(phase__turn__game=game, index=title.start_step - 1).id
        if (title.end_step is not None):
            title.end_step = Step.objects.get(phase__turn__game=game, index=title.end_step - 1).id

        # Save the changes
        title.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rorapp', '0025_title_major_office'),
    ]

    operations = [
        migrations.RunPython(update_title_steps, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='title',
            name='end_step',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ending_title_set', to='rorapp.step'),
        ),
        migrations.AlterField(
            model_name='title',
            name='start_step',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='starting_title_set', to='rorapp.step'),
        ),
    ]
