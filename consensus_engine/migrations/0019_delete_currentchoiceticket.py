# Generated by Django 3.0.4 on 2020-05-06 14:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('consensus_engine', '0018_choiceticket_current'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CurrentChoiceTicket',
        ),
    ]
