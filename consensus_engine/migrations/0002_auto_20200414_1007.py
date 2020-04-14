# Generated by Django 3.0.4 on 2020-04-14 10:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('consensus_engine', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choiceticket',
            name='chooser',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
