# Generated by Django 3.0.4 on 2020-04-07 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proposal_name', models.CharField(max_length=200)),
                ('date_proposed', models.DateTimeField(verbose_name='date proposed')),
            ],
        ),
        migrations.CreateModel(
            name='ChoiceTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_value', models.CharField(max_length=200)),
                ('chooser', models.CharField(max_length=200)),
                ('date_chosen', models.DateTimeField(verbose_name='date chosen')),
                ('proposal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consensus_engine.Proposal')),
            ],
        ),
    ]
