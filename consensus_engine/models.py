from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Proposal(models.Model):
    proposal_name = models.CharField(max_length=200)
    date_proposed = models.DateTimeField('date proposed')
    proposal_caption = models.CharField(max_length=200)
    # properties
    @property
    def short_name(self):
        return (self.proposal_name[:27] + '...') if len(self.proposal_name) > 30 else self.proposal_name
    @property
    def short_caption(self):
        return (self.proposal_caption[:57] + '...') if len(self.proposal_caption) > 60 else self.proposal_caption


class ProposalChoiceManager(models.Manager):
    def activated(self):
        return self.get_queryset().filter(activated_date__isnull=False, deactivated_date__isnull=True)


class ProposalChoice(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    priority = models.IntegerField(null=True)
    activated_date = models.DateTimeField('active date', null=True)
    deactivated_date = models.DateTimeField('deactivated date', null=True)
    objects = ProposalChoiceManager()


class ChoiceTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_chosen = models.DateTimeField('date chosen')
    proposal_choice = models.ForeignKey(ProposalChoice, on_delete=models.CASCADE)


class CurrentChoiceTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    choice_ticket = models.ForeignKey(ChoiceTicket, on_delete=models.CASCADE)
