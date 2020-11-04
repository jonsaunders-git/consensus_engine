from django.db import models, transaction, DataError
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from consensus_engine.utils import ProposalState
from . import GroupMembership, ChoiceTicket, ConsensusHistory
from consensus_engine.exceptions import ProposalStateInvalid


class ProposalManager(models.Manager):
    """ Manager for Proposal data """

    def owned(self, user, states={ProposalState.DRAFT, ProposalState.TRIAL, ProposalState.PUBLISHED,
                                  ProposalState.ON_HOLD, ProposalState.ARCHIVED}):
        return (self.get_queryset().filter(owned_by_id=user.id, state__in=states)
                    .values('id', 'proposal_name', 'proposal_description'))

    def in_group(self, group, states={ProposalState.PUBLISHED}):
        return (self.get_queryset().filter(proposal_group__id=group.id, state__in=states)
                    .values('id', 'proposal_name', 'proposal_description', 'state'))


class Proposal(models.Model):
    proposal_name = models.CharField(max_length=200)
    date_proposed = models.DateTimeField('date proposed')
    proposal_description = models.CharField(max_length=200)
    owned_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                 null=True, blank=True)
    proposal_group = models.ForeignKey('ProposalGroup',
                                       on_delete=models.SET_NULL, null=True)
    state = models.IntegerField(choices=ProposalState.choices(), default=ProposalState.DRAFT)
    # managers
    objects = ProposalManager()

    # class functions
    def get_absolute_url(self):
        return reverse('view_proposal', kwargs={'proposal_id': str(self.pk)})

    def user_can_edit(self, user):
        """ Determines whether the passed in user can edit the proposal """
        can_edit = ((self.owned_by == user)
                    and ((self.state == ProposalState.DRAFT)
                    or (self.state == ProposalState.TRIAL)))
        return can_edit

    def can_vote(self, user):
        # rules:
        # 1. proposal is in state Trial or Published
        # 2. User is a member of the group or the proposal does not have a group
        # 3. User can trial if the Proposal state is Trial or the proposal does not have a group
        if self.proposal_group is None:
            membership_okay = True
            trial_okay = True
        else:
            membership = GroupMembership.objects.filter(group=self.proposal_group, user=user)
            membership_okay = membership.count() == 1
            if membership_okay:
                trial_okay = membership.first().can_trial
            else:
                trial_okay = False
        return ((self.state == ProposalState.PUBLISHED and membership_okay)
                or (self.state == ProposalState.TRIAL and membership_okay and trial_okay))

    def get_total_votes(self):
        total_votes = (ChoiceTicket.objects
                       .filter(proposal_choice__deactivated_date__isnull=True,
                               proposal_choice__proposal=self,
                               state=ProposalState.reporting_as_state(self.state),
                               current=True)
                       .count())
        return total_votes

    def get_active_choices(self, states={ProposalState.PUBLISHED}):
        """ Gets the ProposalChoices that are active currently """
        return self.proposalchoice_set.filter(deactivated_date__isnull=True)

    def determine_consensus(self):
        """ Sets the current consensus across the Proposal Choices on this proposal """
        active_choices = self.get_active_choices()
        # utilise simple - most votes = consensus
        max_votes = 0
        current_consensus = None
        for choice in active_choices:
            choice_votes = choice.current_vote_count
            if choice_votes > max_votes:
                current_consensus = choice
                max_votes = choice_votes
            elif choice_votes == max_votes:  # tie break (no consensus)
                current_consensus = None
        # update all the choices to the new values
        if (current_consensus is None or not current_consensus.current_consensus):
            with transaction.atomic():
                for choice in active_choices:
                    old_value = choice.current_consensus
                    new_value = (choice == current_consensus)  # i.e. only true if is current choice
                    if old_value != new_value:
                        # only update if the state changes
                        choice.current_consensus = new_value
                        choice.save()
        return current_consensus

    def populate_from_template(self, template):
        """ Populates the proposal choices from the template """
        # return if no template selected
        if template is None:
            return
        # deactivate existing choices if there are any
        if self.proposalchoice_set.count() > 0:
            for existing_choice in self.get_active_choices():
                existing_choice.deactivated_date = timezone.now()
                existing_choice.save()
        # create new choices based on the template
        for template_choice in template:
            new_choice = ProposalChoice(proposal=self,
                                        text=template_choice['text'],
                                        priority=template_choice['priority'],
                                        activated_date=timezone.now())
            new_choice.save()

    def get_voting_spread(self, analysis_date=None):
        """ Gets the spread of votes in a dictionary based on the date and time """
        spread = {}
        if(analysis_date is None):
            num_total_votes_cast = self.total_votes
            for choice in self.get_active_choices():
                vote_analysis = {}
                vote_count = choice.current_vote_count
                vote_analysis['text'] = choice.text
                vote_analysis['count'] = vote_count
                if num_total_votes_cast > 0 and vote_count > 0:
                    vote_analysis['percentage'] = (vote_count / num_total_votes_cast) * 100.0
                else:
                    vote_analysis['percentage'] = 0
                spread[choice.id] = vote_analysis
        else:
            historical_data = self.get_consensus_at_datetime(analysis_date).get_consensus_data()
            num_total_votes_cast = sum(item['count'] for item in historical_data)
            for data_element in historical_data:
                vote_analysis = {}
                vote_count = data_element['count']
                vote_analysis['text'] = data_element['text']
                vote_analysis['count'] = vote_count
                if num_total_votes_cast > 0 and vote_count > 0:
                    vote_analysis['percentage'] = (vote_count / num_total_votes_cast) * 100.0
                else:
                    vote_analysis['percentage'] = 0
                spread[data_element['choice_id']] = vote_analysis
        return spread

    def get_consensus_at_datetime(self, request_datetime):
        return ConsensusHistory.objects.at_date(self, request_datetime)

    def updateState(self, state):
        valid_states = self.current_state.get_next_states()
        if state in valid_states:
            self.state = state
            self.save()
        else:
            raise ProposalStateInvalid()

    def draft(self):
        self.updateState(ProposalState.DRAFT)

    def trial(self):
        self.updateState(ProposalState.TRIAL)

    def publish(self, default_group_to_these_choices=False):
        if self.proposal_group:
            if default_group_to_these_choices:
                if self.can_default_group_to_these_choices:
                    # set the group so it knows it has a default
                    self.proposal_group.set_has_default_choices(True)
                    # move all ON_HOLD proposals to archived
                    on_hold_proposals = Proposal.objects.filter(proposal_group=self.proposal_group,
                                                                state=ProposalState.ON_HOLD)
                    for on_hold_proposal in on_hold_proposals:
                        on_hold_proposal.archive()

                else:
                    raise DataError('Default choices cannot be set as Proposal Group has published proposals.')
            else:
                if self.proposal_group.has_default_group_proposal_choices:
                    # deactivate all the existing choices on the proposal
                    (ProposalChoice.objects.filter(proposal=self, deactivated_date__isnull=True)
                                           .update(deactivated_date=timezone.now()))
                    # copy from first published proposal
                    copy_from_proposal = (Proposal.objects
                                          .filter(proposal_group=self.proposal_group, state=ProposalState.PUBLISHED)
                                          .first())
                    if not copy_from_proposal:
                        raise DataError("No default data found")
                    cloned_choices = ProposalChoice.objects.filter(proposal=copy_from_proposal,
                                                                   deactivated_date__isnull=True)
                    for choice in cloned_choices:
                        # use Django method for cloning objects
                        choice.pk = None
                        choice.proposal = self
                        choice.current_consensus = False
                        choice.activated_date = timezone.now()
                        choice.save()
        self.updateState(ProposalState.PUBLISHED)

    def hold(self):
        self.updateState(ProposalState.ON_HOLD)

    def archive(self):
        self.updateState(ProposalState.ARCHIVED)

    # properties
    @property
    def short_name(self):
        return((self.proposal_name[:27] + '...')
               if len(self.proposal_name) > 30
               else self.proposal_name)

    @property
    def total_votes(self):
        reporting_state = ProposalState.reporting_as_state(self.state)
        return (Proposal.objects.filter(id=self.id,
                proposalchoice__choiceticket__current=True, proposalchoice__choiceticket__state=reporting_state)
                .values('proposalchoice__choiceticket__user_id')
                .distinct().count())

    @property
    def current_consensus(self):
        try:
            current_consensus = ProposalChoice.objects.get(deactivated_date__isnull=True,
                                                           proposal=self,
                                                           current_consensus=True)
        except ProposalChoice.DoesNotExist:
            current_consensus = None
        return current_consensus

    @property
    def current_state(self):
        return ProposalState(self.state)

    @property
    def can_default_group_to_these_choices(self):
        return not Proposal.objects.filter(proposal_group=self.proposal_group, state=ProposalState.PUBLISHED)


class ProposalChoiceManager(models.Manager):
    """ Manager for Proposal Choice """

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
    current_consensus = models.BooleanField(default=False, null=False)

    # class functions
    def get_absolute_url(self):
        return reverse('view_proposal', kwargs={'proposal_id': str(self.proposal.id)})

    # properties
    @property
    def current_vote_count(self):
        # counts all the choice tickets for this choice where it is the current choice ticket
        reporting_state = ProposalState.reporting_as_state(self.proposal.state)
        return self.choiceticket_set.filter(current=True, state=reporting_state).count()

    def vote(self, user):
        # reset the current flag on the last vote for this proposal and add another one.
        # -------------------------------------------------------------------------------
        # this function probably doesn't sit here as it doesn't affect the data in the
        # model class (apart from joining to proposal choice) - TODO: Refactor
        # -------------------------------------------------------------------------------
        if self.proposal.can_vote(user):
            with transaction.atomic():
                # important: do not consider state in clearing the previous current
                ChoiceTicket.objects.filter(user=user,
                                            proposal_choice__proposal=self.proposal,
                                            current=True).update(current=False)
                ticket = ChoiceTicket(user=user,
                                      date_chosen=timezone.now(), proposal_choice=self, state=self.proposal.state)
                ticket.save()
                # determine consensus opinion after voting
                self.proposal.determine_consensus()
                # save consensus history
                snapshot = ConsensusHistory.build_snapshot(self.proposal)
                snapshot.save()
        else:
            raise PermissionDenied("Cannot vote in a proposal in this state.")
