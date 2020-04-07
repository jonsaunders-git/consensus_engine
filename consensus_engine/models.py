from django.db import models

# Create your models here.

class Proposal(models.Model):
    proposal_name = models.CharField(max_length=200)
    date_proposed = models.DateTimeField('date proposed')

class ChoiceTicket(models.Model):
    choice_value = models.CharField(max_length=200)
    chooser = models.CharField(max_length=200)
    date_chosen = models.DateTimeField('date chosen')
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
