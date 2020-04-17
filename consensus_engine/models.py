from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Proposal(models.Model):
    proposal_name = models.CharField(max_length=200)
    date_proposed = models.DateTimeField('date proposed')
    proposal_caption = models.CharField(max_length=200)

class ProposalChoice(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    priority = models.IntegerField(null=True)

class ChoiceTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_chosen = models.DateTimeField('date chosen')
    proposal_choice = models.ForeignKey(ProposalChoice, on_delete=models.CASCADE)

class CurrentChoiceTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    choice_ticket = models.ForeignKey(ChoiceTicket, on_delete=models.CASCADE)
