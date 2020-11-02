from django.db import models, DataError
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from consensus_engine.utils import ProposalState
from django.db.models import IntegerField, Value, F, Count
from . import ChoiceTicket, Proposal, GroupMembership, GroupInvite


class ProposalGroupManager(models.Manager):
    """ Manager for Proposal Group data """

    def owned(self, user):
        return self.get_queryset().filter(owned_by_id=user.id)

    def groups_for_member(self, user):
        """
        gets a list of groups that the user is a member of plus
        a count of published proposals they have still to vote on
        """
        # query for a list of current votes
        all_user_choices = ChoiceTicket.objects.filter(current=True, user=user).values('proposal_choice_id')
        # query for a list of all the groups that the user is a member of
        groups_member_of = ProposalGroup.objects.filter(groupmembership__user=user)
        # query for a list of published proposals that the user has a current vote on
        proposals_voted_for = Proposal.objects.filter(proposalchoice__deactivated_date__isnull=True,
                                                      proposalchoice__id__in=all_user_choices,
                                                      state=ProposalState.PUBLISHED,
                                                      proposal_group__in=groups_member_of).values('id')
        # query for a list of published proposals that the user does not have a current vote on
        proposals_not_voted_for = (Proposal.objects
                                   .filter(proposal_group__in=groups_member_of, state=ProposalState.PUBLISHED)
                                   .exclude(id__in=proposals_voted_for)
                                   )
        # query for a list of the groups that votes are needed on for published proposals
        groups_votes_needed = (proposals_not_voted_for
                               .values('proposal_group__id', 'proposal_group__group_name')
                               .annotate(id=F('proposal_group_id'), group_name=F('proposal_group__group_name'))
                               .values('id', 'group_name')
                               .annotate(propcount=Count('id'))
                               .values('id', 'group_name', 'propcount')
                               )
        # query for list of the ids of the proposals that need votes, to exclude in the next query
        groups_votes_needed_ids = groups_votes_needed.values('id')
        # query for all the groups that do not have proposals that need the user to vote
        groups_no_votes_needed = (self.get_queryset()
                                  .filter(groupmembership__user=user)
                                  .exclude(id__in=groups_votes_needed_ids)
                                  .annotate(propcount=Value(0, output_field=IntegerField()))
                                  .values('id', 'group_name', 'propcount'))
        # query that unions the groups that need votes with the group that does not need a vote
        all_groups_member_of = groups_votes_needed.union(groups_no_votes_needed).order_by('group_name')
        # returns a single query (not yet executed that has all the detail above)
        return all_groups_member_of

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

    def is_user_part_of_trial(self, user):
        return GroupMembership.objects.filter(user=user, group=self, can_trial=True).count() == 1

    def has_user_been_invited(self, user):
        return GroupInvite.objects.filter(invitee=user, group=self, accepted=None).count() == 1

    def join_group(self, user, can_trial=False):
        if not self.is_user_member(user):
            membership = GroupMembership(user=user, group=self, date_joined=timezone.now(), can_trial=can_trial)
            membership.save()
        else:
            raise DataError("User is already a member of this group.")

    def invite_user(self, inviter_user, invitee_user, allow_trials=False):
        if not self.is_user_member(inviter_user):
            raise PermissionDenied("Inviter is not a member of the group")
        if self.is_user_member(invitee_user):
            raise DataError("User is already a member of this group")
        if self.has_user_been_invited(invitee_user):
            raise DataError("User has already been invited")
        invite = GroupInvite(group=self, invitee=invitee_user,
                             inviter=inviter_user,
                             can_trial=allow_trials,
                             invite_date_time=timezone.now())
        invite.save()
        return invite

    def get_members(self):
        return GroupMembership.objects.filter(group=self)

    def deactivate_votes_for_user_in_group(self, user):
        ChoiceTicket.objects.filter(proposal_choice__proposal__proposal_group=self,
                                    user=user).update(current=False)

    def remove_member(self, user):
        if user == self.owned_by:
            raise PermissionDenied("Cannot remove the owner of the proposal group from the group.")
        # removing members - need to remove the votes too!
        try:
            removed_membership = GroupMembership.objects.get(group=self, user=user)
            self.deactivate_votes_for_user_in_group(user)
            removed_membership.delete()
        except GroupMembership.DoesNotExist:
            raise DataError("User is not a member of the group and cannot be removed")

    # properties
    @property
    def short_name(self):
        return ((self.group_name[:27] + '...')
                if len(self.group_name) > 30
                else self.group_name)
