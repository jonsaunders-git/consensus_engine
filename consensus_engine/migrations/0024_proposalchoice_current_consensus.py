# Generated by Django 3.0.4 on 2020-06-02 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consensus_engine', '0023_remove_proposal_current_consensus'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposalchoice',
            name='current_consensus',
            field=models.BooleanField(default=False),
        ),
    ]
