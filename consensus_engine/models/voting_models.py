from django.db import models
from django.contrib.auth.models import User
from consensus_engine.utils import ProposalState


class ChoiceTicketManager(models.Manager):
    """ Manager for Choice Ticket data """

    def my_votes(self, user):
        return (ChoiceTicket.objects.filter(current=True,
                                            user=user,
                                            proposal_choice__deactivated_date__isnull=True,
                                            )
                .annotate(choice_text=models.F('proposal_choice__text'))
                .annotate(proposal_id=models.F('proposal_choice__proposal__id'))
                .annotate(proposal_name=models.F('proposal_choice__proposal__proposal_name'))
                .annotate(proposal_group=models.F('proposal_choice__proposal__proposal_group__group_name'))
                .values('proposal_id', 'proposal_name',
                        'choice_text', 'proposal_group')
                .order_by('proposal_group', 'proposal_name'))

    def get_current_choice(self, user, proposal):
        # if the proposal state trial show the trial data otherwise always show published.
        reporting_state = ProposalState.reporting_as_state(proposal.state)
        try:
            current_choice = (ChoiceTicket.objects
                              .get(user=user,
                                   proposal_choice__proposal=proposal,
                                   current=True, state=reporting_state))
        except (KeyError, ChoiceTicket.DoesNotExist):
            current_choice = None
        return current_choice


class ChoiceTicket(models.Model):
    """ Defines a specific choice at a specific time """
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                             null=True, blank=True)
    date_chosen = models.DateTimeField('date chosen')
    proposal_choice = models.ForeignKey('ProposalChoice',
                                        on_delete=models.CASCADE)
    current = models.BooleanField(default=True, null=True)
    state = models.IntegerField(choices=ProposalState.choices(), default=ProposalState.PUBLISHED)
    objects = ChoiceTicketManager()
