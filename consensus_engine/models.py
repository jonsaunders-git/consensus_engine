from django.db import models, transaction, DataError
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import PermissionDenied


class GroupMembership(models.Model):
    """ Defines membership of Groups """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    group = models.ForeignKey('ProposalGroup', on_delete=models.CASCADE, null=False)
    date_joined = models.DateTimeField('date joined')


class GroupInviteManager(models.Manager):
    """ Manager for Group Invites """
    def my_open_invites(self, user):
        return self.get_queryset().filter(invitee=user, accepted=None)

    def my_open_invites_count(self, user):
        return self.my_open_invites(user).count()

    # To implement when needed
    # def my_accepted_invites(self, user):
    #    return self.get_queryset().filter(invitee=user, accepted=True)
    #
    # def my_declined_invites(self, user):
    #    return self.get_queryset().filter(invitee=user, accepted=True)
    #
    # def my_open_send_invitations(self, user):
    #    return self.get_queryset().filter(inviter=user, accepted=None)


class GroupInvite(models.Model):
    """ Defines an invite to a Group """
    group = models.ForeignKey('ProposalGroup', on_delete=models.CASCADE, null=False)
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="invites")
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="invited")
    invite_date_time = models.DateTimeField('date invited', null=False)
    # accepted - True = accepted, False=declined, null=Neither accepted or declined
    accepted = models.BooleanField(null=True)
    date_accepted_or_declined = models.DateTimeField('date accepted or declined', null=True)
    # managers
    objects = GroupInviteManager()

    def accept(self):
        with transaction.atomic():
            self.accepted = True
            self.date_accepted_or_declined = timezone.now()
            self.group.join_group(self.invitee)
            self.save()

    def decline(self):
        with transaction.atomic():
            self.accepted = False
            self.date_accepted_or_declined = timezone.now()
            self.save()


class ProposalGroupManager(models.Manager):
    """ Manager for Proposal Group data """
    def owned(self, user):
        return self.get_queryset().filter(owned_by_id=user.id)

    def groups_for_member(self, user):
        return self.get_queryset().filter(groupmembership__user=user)

    def list_of_membership(self, user):
        return self.get_queryset().filter(groupmembership__user=user).values_list('id', flat=True)


class ProposalGroup(models.Model):
    """ Top level grouping for Proposals """
    group_name = models.CharField(max_length=200)
    owned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group_description = models.CharField(max_length=200, null=True)
    # managers
    objects = ProposalGroupManager()

    # class functions
    def get_absolute_url(self):
        return reverse('group_proposals', kwargs={'proposal_group_id': str(self.pk)})

    def is_user_member(self, user):
        return GroupMembership.objects.filter(user=user, group=self).count() == 1

    def has_user_been_invited(self, user):
        return GroupInvite.objects.filter(invitee=user, group=self, accepted=None).count() == 1

    def join_group(self, user):
        if not self.is_user_member(user):
            membership = GroupMembership(user=user, group=self, date_joined=timezone.now())
            membership.save()
        else:
            raise DataError("User is already a member of this group.")

    def invite_user(self, inviter_user, invitee_user):
        if not self.is_user_member(inviter_user):
            raise PermissionDenied("Inviter is not a member of the group")
        if self.is_user_member(invitee_user):
            raise DataError("User is already a member of this group")
        if self.has_user_been_invited(invitee_user):
            raise DataError("User has already been invited")
        invite = GroupInvite(group=self, invitee=invitee_user,
                             inviter=inviter_user,
                             invite_date_time=timezone.now())
        invite.save()
        return invite

    # properties
    @property
    def short_name(self):
        return ((self.group_name[:27] + '...')
                if len(self.group_name) > 30
                else self.group_name)


class ProposalManager(models.Manager):
    """ Manager for Proposal data """
    def owned(self, user):
        return (self.get_queryset().filter(owned_by_id=user.id)
                    .values('id', 'proposal_name', 'proposal_description'))

    def in_group(self, group):
        return (self.get_queryset().filter(proposal_group__id=group.id)
                    .values('id', 'proposal_name', 'proposal_description'))


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

    # class functions
    def get_absolute_url(self):
        return reverse('view_proposal', kwargs={'proposal_id': str(self.pk)})

    def user_can_edit(self, user):
        """ Determines whether the passed in user can edit the proposal """
        return self.owned_by == user

    def get_active_choices(self):
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
        if (current_consensus is None or
                not current_consensus.current_consensus):  # short cut - no update if no change
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
                vote_analysis["text"] = choice.text
                vote_analysis["count"] = vote_count
                if num_total_votes_cast > 0 and vote_count > 0:
                    vote_analysis["percentage"] = (vote_count / num_total_votes_cast) * 100.0
                else:
                    vote_analysis["percentage"] = 0
                spread[choice.id] = vote_analysis
        return spread

    # properties
    @property
    def short_name(self):
        return((self.proposal_name[:27] + '...')
               if len(self.proposal_name) > 30
               else self.proposal_name)

    @property
    def total_votes(self):
        return (Proposal.objects.filter(id=self.id,
                proposalchoice__choiceticket__current=True)
                .values('proposalchoice__choiceticket__user_id')
                .distinct().count())


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
        return self.choiceticket_set.filter(current=True).count()

    def vote(self, user):
        # reset the current flag on the last vote for this proposal and add another one.
        # -------------------------------------------------------------------------------
        # this function probably doesn't sit here as it doesn't affect the data in the
        # model class (apart from joining to proposal choice) - TODO: Refactor
        # -------------------------------------------------------------------------------
        with transaction.atomic():
            ChoiceTicket.objects.filter(user=user,
                                        proposal_choice__proposal=self.proposal,
                                        current=True).update(current=False)
            ticket = ChoiceTicket(user=user,
                                  date_chosen=timezone.now(), proposal_choice=self)
            ticket.save()
            # determine consensus opinion after voting
            self.proposal.determine_consensus()


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
        try:
            current_choice = (ChoiceTicket.objects
                              .get(user=user,
                                   proposal_choice__proposal=proposal,
                                   current=True))
        except (KeyError, ChoiceTicket.DoesNotExist):
            current_choice = None
        return current_choice


class ChoiceTicket(models.Model):
    """ Defines a specific choice at a specific time """
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                             null=True, blank=True)
    date_chosen = models.DateTimeField('date chosen')
    proposal_choice = models.ForeignKey(ProposalChoice,
                                        on_delete=models.CASCADE)
    current = models.BooleanField(default=True, null=True)
    objects = ChoiceTicketManager()
