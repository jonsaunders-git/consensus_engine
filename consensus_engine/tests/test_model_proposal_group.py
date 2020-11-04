from django.test import TestCase
from django.db import DataError
from .mixins import TwoUserMixin, ProposalGroupMixin, ProposalTestHelper
from consensus_engine.models import ProposalGroup, Proposal, ChoiceTicket, ProposalChoice
from django.core.exceptions import PermissionDenied
from consensus_engine.utils import ProposalState
from django.utils import timezone


# models test
class ProposalGroupTest(TwoUserMixin, ProposalGroupMixin, TestCase):

    def test_proposal_group_creation(self):
        pg = self.create_proposal_group()
        self.assertTrue(isinstance(pg, ProposalGroup))
        self.assertTrue(pg.group_name == "test group")
        self.assertTrue(pg.owned_by == self.user)
        self.assertTrue(pg.group_description == "it's only a test group")

    def test_proposal_group_short_name(self):
        w = self.create_proposal_group(group_name="it's only a test group")
        self.assertTrue(w.short_name == "it's only a test group")
        y = self.create_proposal_group(group_name="this is a long test name anxyz")
        self.assertTrue(y.short_name == "this is a long test name anxyz")
        x = self.create_proposal_group(group_name="this is a long test name and should be truncated")
        self.assertTrue(x.short_name == "this is a long test name an...")

    def test_proposal_group_owned_set(self):
        # should be no proposals for this user at start of test
        self.assertTrue(ProposalGroup.objects.owned(self.user).count() == 0)
        # add one
        _ = self.create_proposal_group()
        self.assertTrue(ProposalGroup.objects.owned(self.user).count() == 1)
        # add another
        _ = self.create_proposal_group()
        self.assertTrue(ProposalGroup.objects.owned(self.user).count() == 2)
        # add one for the secind user
        _ = self.create_proposal_group(owned_by=self.user2)
        # two for user 1 and 1 for user 2
        self.assertTrue(ProposalGroup.objects.owned(self.user).count() == 2)
        self.assertTrue(ProposalGroup.objects.owned(self.user2).count() == 1)

    def test_join_proposal_group(self):
        pg = self.create_proposal_group()
        # get a list of groups that user is in
        ml = ProposalGroup.objects.list_of_membership(self.user)
        self.assertTrue(pg.id in ml)
        # add second user to proposal group
        pg.join_group(self.user2)
        pg2 = self.create_proposal_group()
        l2 = ProposalGroup.objects.list_of_membership(self.user2)
        self.assertTrue(pg.id in l2)
        self.assertTrue(pg2.id not in l2)
        self.assertTrue(pg.id in l2)
        self.assertTrue(ProposalGroup.objects.groups_for_member(self.user).count() == 2)
        self.assertTrue(ProposalGroup.objects.groups_for_member(self.user2).count() == 1)
        # test rejoining same group_proposals
        with self.assertRaises(DataError):
            pg.join_group(self.user)

    def test_list_group_members(self):
        pg = self.create_proposal_group()
        ml = pg.get_members()
        self.assertTrue(len(ml) == 1)
        self.assertTrue(ml.first().id == self.user.id)
        pg.join_group(self.user2)
        ml2 = pg.get_members()
        self.assertTrue(len(ml2) == 2)
        self.assertTrue(ml.first().id == self.user.id)
        self.assertTrue(ml.last().id == self.user2.id)

    def test_remove_group_member(self):
        pg = self.create_proposal_group()
        pg.join_group(self.user2)
        ml = pg.get_members()
        self.assertTrue(len(ml) == 2)
        pg.remove_member(self.user2)
        ml2 = pg.get_members()
        self.assertTrue(len(ml2) == 1)
        self.assertTrue(ml.first().id == self.user.id)
        with self.assertRaises(PermissionDenied):
            pg.remove_member(pg.owned_by)

    def test_remove_group_non_member(self):
        pg = self.create_proposal_group()
        with self.assertRaises(DataError, msg="User is not a member of the group and cannot be removed"):
            pg.remove_member(self.user2)

    def test_remove_group_member_votes(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        p.publish()
        # check that total votes = 0 if there are no votes
        self.assertTrue(isinstance(p, Proposal))
        self.assertTrue(p.total_votes == 0)
        pc1 = p.proposalchoice_set.first()
        _ = p.proposalchoice_set.last()
        v = ChoiceTicket.objects.create(user=self.user, date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(p.total_votes == 1)
        pg.join_group(self.user2)
        _ = ChoiceTicket.objects.create(user=self.user2, date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(p.total_votes == 2)
        ml = pg.get_members()
        self.assertTrue(len(ml) == 2)
        pg.remove_member(self.user2)
        self.assertTrue(p.total_votes == 1)
        ml2 = pg.get_members()
        self.assertTrue(len(ml2) == 1)
        self.assertTrue(ml.first().id == self.user.id)

    def test_can_vote_group_no_user2(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.trial()
        self.assertTrue(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.publish()
        self.assertTrue(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.hold()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.archive()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))

    def test_can_vote_group_no_trial(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.trial()
        pg.join_group(self.user2)
        self.assertTrue(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.publish()
        self.assertTrue(p.can_vote(self.user))
        self.assertTrue(p.can_vote(self.user2))
        p.hold()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.archive()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))

    def test_can_vote_group_trial(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.trial()
        pg.join_group(self.user2, True)
        self.assertTrue(p.can_vote(self.user))
        self.assertTrue(p.can_vote(self.user2))
        p.publish()
        self.assertTrue(p.can_vote(self.user))
        self.assertTrue(p.can_vote(self.user2))
        p.hold()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.archive()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))

    def test_can_vote_group_trial_remove(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.trial()
        pg.join_group(self.user2, True)
        self.assertTrue(p.can_vote(self.user))
        self.assertTrue(p.can_vote(self.user2))
        pg.remove_member(self.user2)
        self.assertTrue(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.publish()
        self.assertTrue(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.hold()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.archive()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))

    def test_can_vote_group_no_trial_remove(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.trial()
        pg.join_group(self.user2, False)
        self.assertTrue(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.publish()
        self.assertTrue(p.can_vote(self.user))
        self.assertTrue(p.can_vote(self.user2))
        pg.remove_member(self.user2)
        self.assertTrue(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.hold()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))
        p.archive()
        self.assertFalse(p.can_vote(self.user))
        self.assertFalse(p.can_vote(self.user2))

    def test_group_member_list_proposals_to_be_voted_on_simple(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        p.trial()
        groups_for_member = ProposalGroup.objects.groups_for_member(self.user)
        self.assertTrue(groups_for_member.count() == 1)
        self.assertTrue(groups_for_member.first()['propcount'] == 0)
        p.publish()
        groups_for_member = ProposalGroup.objects.groups_for_member(self.user)
        self.assertTrue(groups_for_member.count() == 1)
        self.assertTrue(groups_for_member.first()['propcount'] == 1)
        p.hold()
        groups_for_member = ProposalGroup.objects.groups_for_member(self.user)
        self.assertTrue(groups_for_member.count() == 1)
        self.assertTrue(groups_for_member.first()['propcount'] == 0)
        p.archive()
        groups_for_member = ProposalGroup.objects.groups_for_member(self.user)
        self.assertTrue(groups_for_member.count() == 1)
        self.assertTrue(groups_for_member.first()['propcount'] == 0)

    def test_group_member_list_proposals_to_be_voted_on_two_users(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        p.trial()
        g1 = ProposalGroup.objects.groups_for_member(self.user)
        self.assertTrue(g1.count() == 1)
        self.assertTrue(g1.first()['propcount'] == 0)
        g2 = ProposalGroup.objects.groups_for_member(self.user2)
        self.assertTrue(g2.count() == 0)
        pg.join_group(self.user2, False)
        g3 = ProposalGroup.objects.groups_for_member(self.user2)
        self.assertTrue(g3.count() == 1)
        self.assertTrue(g3.first()['propcount'] == 0)
        p.publish()
        g4 = ProposalGroup.objects.groups_for_member(self.user)
        self.assertTrue(g4.count() == 1)
        self.assertTrue(g4.first()['propcount'] == 1)
        g5 = ProposalGroup.objects.groups_for_member(self.user2)
        self.assertTrue(g5.count() == 1)
        self.assertTrue(g5.first()['propcount'] == 1)
        pg.remove_member(self.user2)
        g6 = ProposalGroup.objects.groups_for_member(self.user2)
        self.assertTrue(g6.count() == 0)
        p.hold()
        g7 = ProposalGroup.objects.groups_for_member(self.user)
        self.assertTrue(g7.count() == 1)
        self.assertTrue(g7.first()['propcount'] == 0)
        p.archive()
        g8 = ProposalGroup.objects.groups_for_member(self.user)
        self.assertTrue(g8.count() == 1)
        self.assertTrue(g8.first()['propcount'] == 0)

    def test_default_group_choices(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        p.trial()
        p.publish(default_group_to_these_choices=True)
        p2 = ProposalTestHelper.new_proposal(proposal_group=pg, owned_by=self.user,
                                             date_proposed=timezone.now())
        p2.publish()
        self.assertTrue(ProposalChoice.objects.filter(proposal=p2, deactivated_date__isnull=True).count() == 2)

    def test_no_default_group_choices(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        p.trial()
        p.publish(default_group_to_these_choices=False)
        p2 = ProposalTestHelper.new_proposal(proposal_group=pg, owned_by=self.user,
                                             date_proposed=timezone.now())
        p2.publish()
        self.assertTrue(ProposalChoice.objects.filter(proposal=p2).count() == 0)
        p3 = ProposalTestHelper.new_proposal_with_two_choices(proposal_group=pg, owned_by=self.user,
                                                              date_proposed=timezone.now())
        p3.publish()
        self.assertTrue(ProposalChoice.objects.filter(proposal=p3, deactivated_date__isnull=True).count() == 2)

    def test_default_group_choices_on_hold(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        p.hold()
        self.assertTrue(Proposal.objects.filter(state=ProposalState.ON_HOLD).count() == 1)
        p2 = ProposalTestHelper.new_proposal_with_two_choices(proposal_group=pg, owned_by=self.user,
                                                              date_proposed=timezone.now())
        p2.publish(default_group_to_these_choices=True)
        self.assertTrue(Proposal.objects.filter(state=ProposalState.ON_HOLD).count() == 0)
        self.assertTrue(Proposal.objects.filter(state=ProposalState.ARCHIVED).count() == 1)
        self.assertTrue(ProposalChoice.objects.filter(proposal=p2).count() == 2)
        p3 = ProposalTestHelper.new_proposal_with_two_choices(proposal_group=pg, owned_by=self.user,
                                                              date_proposed=timezone.now())
        p3.publish()
        self.assertTrue(ProposalChoice.objects.filter(proposal=p3, deactivated_date__isnull=True).count() == 2)

    def test_default_group_choices_permission_failed(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        p.publish(default_group_to_these_choices=False)
        p2 = ProposalTestHelper.new_proposal(proposal_group=pg, owned_by=self.user,
                                             date_proposed=timezone.now())
        with (self
              .assertRaises(DataError,
                            msg='Default choices cannot be set as Proposal Group has published proposals.')):
            p2.publish(default_group_to_these_choices=(True))

    def test_no_data_clone_choices(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        pg.group_default_choices = True
        pg.save
        with self.assertRaises(DataError, msg="No default data found"):
            p.publish()

    def test_try_to_default_with_published_proposals(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        p.publish(default_group_to_these_choices=(True))
        with self.assertRaises(DataError,
                               msg="Default choices cannot be set as Proposal Group has published proposals."):
            pg.set_has_default_choices(True)
