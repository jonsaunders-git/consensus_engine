from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User

from .mixins import TwoUserMixin, ProposalMixin

# Create your tests here.

from consensus_engine.models import Proposal, ProposalChoice, ChoiceTicket, ProposalGroup
from django.utils import timezone


# models test
class ProposalTest(TwoUserMixin, ProposalMixin, TestCase):

    def test_proposal_creation(self):
        w = self.create_new_proposal()
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(w.date_proposed <= timezone.now())
        self.assertTrue(w.proposal_name == "only a test")
        self.assertTrue(w.proposal_description == "yes, this is only a test")
        self.assertTrue(w.owned_by == self.user)

    def test_proposal_short_name(self):
        w = self.create_new_proposal()
        self.assertTrue(w.short_name == "only a test")
        x = self.create_new_proposal(proposal_name="this is a long test name and should be truncated")
        self.assertTrue(x.short_name == "this is a long test name an...")
        x = self.create_new_proposal(proposal_name="this is a long test name anxyz")
        self.assertTrue(x.short_name == "this is a long test name anxyz")

    def test_total_votes_for_new_proposal(self):
        w = self.create_new_proposal()
        self.assertTrue(w.total_votes == 0)

    def test_proposal_creation_with_two_proposal_choices(self):
        w = self.create_proposal_with_two_proposal_choices()
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(w.proposalchoice_set.count() == 2)
        pc1 = w.proposalchoice_set.first()
        self.assertTrue(isinstance(pc1, ProposalChoice))
        pc2 = w.proposalchoice_set.last()
        self.assertTrue(isinstance(pc2, ProposalChoice))

    def test_total_votes_for_proposal_with_two_proposal_choices_with_voting(self):
        w = self.create_proposal_with_two_proposal_choices()
        # check that total votes = 0 if there are no votes
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(w.total_votes == 0)
        pc1 = w.proposalchoice_set.first()
        pc2 = w.proposalchoice_set.last()
        v = ChoiceTicket.objects.create(user=self.user, date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(w.total_votes == 1)
        # change votes - change current
        v2 = ChoiceTicket.objects.create(user=self.user, date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        v.current=False;
        v.save();
        self.assertTrue(w.total_votes == 1)
        # create a vote by another user and test that we have two votes
        v3 = ChoiceTicket.objects.create(user=self.user2, date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(w.total_votes == 2)

    def test_total_votes_for_proposal_with_a_deactivated_proposal_choice(self):
        w = self.create_proposal_with_two_proposal_choices()
        # check that total votes = 0 if there are no votes
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(w.total_votes == 0)
        pc1 = w.proposalchoice_set.first()
        pc2 = w.proposalchoice_set.last()
        v = ChoiceTicket.objects.create(user=self.user, date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(w.total_votes == 1)
        # change votes - change current
        v2 = ChoiceTicket.objects.create(user=self.user, date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        v.current=False;
        v.save();
        self.assertTrue(w.total_votes == 1)
        # create a vote by another user and test that we have two votes
        v3 = ChoiceTicket.objects.create(user=self.user2, date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(w.total_votes == 2)


    def test_proposal_owned_set(self):
        # should be no proposals for this user at start of test
        self.assertTrue(Proposal.objects.owned(self.user).count() == 0)
        # add one
        p = self.create_new_proposal()
        self.assertTrue(Proposal.objects.owned(self.user).count() == 1)
        # add another
        p1 = self.create_new_proposal()
        self.assertTrue(Proposal.objects.owned(self.user).count() == 2)
        # add one for the secind user
        p2 = self.create_new_proposal(owned_by=self.user2)
        # two for user 1 and 1 for user 2
        self.assertTrue(Proposal.objects.owned(self.user).count() == 2)
        self.assertTrue(Proposal.objects.owned(self.user2).count() == 1)

    def test_proposal_in_group_creation(self):
        g = ProposalGroup.objects.create(group_name="Test Group", owned_by=self.user, group_description="it's only a test group")
        w = self.create_new_proposal(proposal_group=g)
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(w.date_proposed <= timezone.now())
        self.assertTrue(w.proposal_name == "only a test")
        self.assertTrue(w.proposal_description == "yes, this is only a test")
        self.assertTrue(w.owned_by == self.user)

    def test_proposal_in_group_set(self):
        g = ProposalGroup.objects.create(group_name="Test Group", owned_by=self.user, group_description="it's only a test group")
        # should be no proposals for this user at start of test
        self.assertTrue(Proposal.objects.in_group(g).count() == 0)
        # add one
        p = self.create_new_proposal(proposal_group=g)
        self.assertTrue(Proposal.objects.in_group(g).count() == 1)
        # add another
        p1 = self.create_new_proposal(proposal_group=g)
        self.assertTrue(Proposal.objects.in_group(g).count() == 2)
        g2 = ProposalGroup.objects.create(group_name="Test Group 2", owned_by=self.user, group_description="it's only a test group")
        # add one for the second group
        p2 = self.create_new_proposal(proposal_group=g2)
        # two for group 1 and 1 for group 2
        self.assertTrue(Proposal.objects.in_group(g).count() == 2)
        self.assertTrue(Proposal.objects.in_group(g2).count() == 1)
