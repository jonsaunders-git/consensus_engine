# Generated by Django 3.0.4 on 2020-06-02 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('consensus_engine', '0022_proposal_current_consensus'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposal',
            name='current_consensus',
        ),
    ]
