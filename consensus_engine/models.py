from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class ProposalGroupManager(models.Manager):
    def owned(self, user):
        return self.get_queryset().filter(owned_by_id=user.id)


class ProposalGroup(models.Model):
    group_name = models.CharField(max_length=200)
    owned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group_description = models.CharField(max_length=200, null=True)
    # managers
    objects = ProposalGroupManager()
    # properties
    @property
    def short_name(self):
        return ((self.group_name[:27] + '...')
                if len(self.group_name) > 30
                else self.group_name)

class ProposalManager(models.Manager):
    def owned(self, user):
        return (self.get_queryset().filter(owned_by_id=user.id)
                    .values('id','proposal_name', 'proposal_description' ))
    def in_group(self, group):
        return (self.get_queryset().filter(proposal_group__id=group.id)
                    .values('id','proposal_name', 'proposal_description'))


class Proposal(models.Model):
    proposal_name = models.CharField(max_length=200)
    date_proposed = models.DateTimeField('date proposed')
    proposal_description = models.CharField(max_length=200)
    owned_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    proposal_group = models.ForeignKey(ProposalGroup,
                                        on_delete=models.SET_NULL, null=True)
    # managers
    objects = ProposalManager()
    # properties
    @property
    def short_name(self):
        return ((self.proposal_name[:27] + '...')
            if len(self.proposal_name) > 30
            else self.proposal_name)
    @property
    def total_votes(self):
        return (Proposal.objects.filter(id=self.id,
                    proposalchoice__choiceticket__isnull=False)
                    .values('proposalchoice__choiceticket__user_id')
                    .distinct().count())

class ProposalChoiceManager(models.Manager):
    def activated(self):
        return (self.get_queryset()
            .filter(activated_date__isnull=False,
                deactivated_date__isnull=True))


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
        return self.choiceticket_set.filter(current=True).count()
    def vote(self, user):
        # reset the current flag on the last vote for this proposal and add another one.
        # -------------------------------------------------------------------------------
        # this function probably doesn't sit here as it doesn't affect the data in the
        # model class (apart from joining to proposal choice) - TODO: Refactor
        # -------------------------------------------------------------------------------
        with transaction.atomic():
            ChoiceTicket.objects.filter(user = user,
                proposal_choice__proposal = self.proposal,
                current=True).update(current=False)
            ticket = ChoiceTicket(user=user,
                        date_chosen=timezone.now(), proposal_choice=self)
            ticket.save()

class ChoiceTicketManager(models.Manager):
    
    def my_votes(self, user):
        return (ChoiceTicket.objects.filter(
                            current=True,
                            user=user,
                            proposal_choice__deactivated_date__isnull=True,
                            )
            .annotate(choice_text=models.F('proposal_choice__text'))
            .annotate(proposal_id=models.F('proposal_choice__proposal__id'))
            .annotate(proposal_name=
                models.F('proposal_choice__proposal__proposal_name'))\
            .annotate(proposal_group=
                models.F('proposal_choice__proposal__proposal_group__group_name'))\
            .values('proposal_id', 'proposal_name',
                'choice_text', 'proposal_group')
            .order_by('proposal_group', 'proposal_name'))

    def get_current_choice(self, user, proposal):
        try:
            current_choice = ChoiceTicket.objects.get(user = user, proposal_choice__proposal = proposal, current = True)
        except (KeyError, ChoiceTicket.DoesNotExist):
            current_choice = None
        return current_choice


class ChoiceTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    date_chosen = models.DateTimeField('date chosen')
    proposal_choice = models.ForeignKey(ProposalChoice,
                                            on_delete=models.CASCADE)
    current = models.BooleanField(default=True, null=True)
    objects = ChoiceTicketManager()
