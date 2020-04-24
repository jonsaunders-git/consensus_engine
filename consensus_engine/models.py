from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ProposalGroupManager(models.Manager):
    def owned(self, user):
        return self.get_queryset().filter(owned_by_id=user.id)


class ProposalGroup(models.Model):
    group_name = models.CharField(max_length=200)
    owned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # managers
    objects = ProposalGroupManager()


class ProposalManager(models.Manager):
    def activated(self):
        return self.get_queryset().filter(proposalchoice__isnull=False,proposalchoice__deactivated_date__isnull=True).distinct()
    def owned(self, user):
        return self.get_queryset().filter(owned_by_id=user.id)
    def in_group(self, group):
        return self.get_queryset().filter(proposal_group__id=group.id)
    def myvotes(self, user):
        # work down the relationships to only get the chocie name of the one selected by the user - rename the field using the F method
        return self.get_queryset().filter(currentchoiceticket__user_id=user.id)\
            .exclude(proposalchoice__deactivated_date__isnull=False)\
            .annotate(choice_text=models.F('currentchoiceticket__choice_ticket__proposal_choice__text'))\
            .values('id','proposal_name','choice_text')


class Proposal(models.Model):
    proposal_name = models.CharField(max_length=200)
    date_proposed = models.DateTimeField('date proposed')
    proposal_caption = models.CharField(max_length=200)
    owned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    proposal_group = models.ForeignKey(ProposalGroup, on_delete=models.SET_NULL, null=True)
    # managers
    objects = ProposalManager()
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
    # properties
    @property
    def current_vote_count(self):
        # counts all the choice tickets for this choice where it is the current choice ticket
        return self.choiceticket_set.filter(currentchoiceticket__isnull=False).count()


class ChoiceTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_chosen = models.DateTimeField('date chosen')
    proposal_choice = models.ForeignKey(ProposalChoice, on_delete=models.CASCADE)


class CurrentChoiceTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    choice_ticket = models.ForeignKey(ChoiceTicket, on_delete=models.CASCADE)
