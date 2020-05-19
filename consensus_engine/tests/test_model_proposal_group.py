from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User

from .mixins import TwoUserMixin, ProposalGroupMixin

# Create your tests here.

from django.test import TestCase
from consensus_engine.models import Proposal, ProposalChoice, ChoiceTicket, ProposalGroup
from django.utils import timezone


# models test
class ProposalGroupTest(TwoUserMixin, ProposalGroupMixin, TestCase):

    def test_proposal_group_creation(self):
        pg =self.create_proposal_group()
        self.assertTrue(isinstance(pg,ProposalGroup))
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
        p = self.create_proposal_group()
        self.assertTrue(ProposalGroup.objects.owned(self.user).count() == 1)
        # add another
        p1 = self.create_proposal_group()
        self.assertTrue(ProposalGroup.objects.owned(self.user).count() == 2)
        # add one for the secind user
        p2 = self.create_proposal_group(owned_by=self.user2)
        # two for user 1 and 1 for user 2
        self.assertTrue(ProposalGroup.objects.owned(self.user).count() == 2)
        self.assertTrue(ProposalGroup.objects.owned(self.user2).count() == 1)
