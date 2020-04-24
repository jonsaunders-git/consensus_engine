# Generated by Django 3.0.4 on 2020-04-24 10:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('consensus_engine', '0015_proposal_proposal_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposalgroup',
            name='owned_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]