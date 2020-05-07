from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User

# Create your tests here.

from django.test import TestCase
from consensus_engine.models import Proposal, ProposalChoice, ChoiceTicket, ProposalGroup
from django.utils import timezone


# models test
class ProposalChoiceTest(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        self.user2 = User.objects.create_user(
            username='jacob2', email='jacob@…', password='top_secret')
        self.proposal = Proposal.objects.create(proposal_name="Test Proposal", date_proposed=timezone.now(),
            proposal_description="This is a test proposal description", owned_by=self.user, proposal_group=None)

    def create_new_proposal_choice(self, proposal=None, text="This is a choice", priority=100,
        activated_date=timezone.now(), deactivated_date=None):
        if proposal == None:
            proposal = self.proposal;
        return ProposalChoice.objects.create(proposal=proposal, text=text, priority=priority,
            activated_date=activated_date, deactivated_date=deactivated_date)

    def test_proposal_choice_creation(self):
        pc = self.create_new_proposal_choice()
        self.assertTrue(isinstance(pc, ProposalChoice))
        self.assertTrue(pc.proposal == self.proposal)
        self.assertTrue(pc.text == "This is a choice")
        self.assertTrue(pc.activated_date<=timezone.now())
        self.assertTrue(pc.deactivated_date == None)

    def test_proposal_choice_activated_set(self):
        self.assertTrue(ProposalChoice.objects.activated().count() == 0)
        pc = self.create_new_proposal_choice()
        self.assertTrue(ProposalChoice.objects.activated().count() == 1)
        pc2 = self.create_new_proposal_choice()
        self.assertTrue(ProposalChoice.objects.activated().count() == 2)
        # deactivate pc
        pc.deactivated_date = timezone.now()
        pc.save();
        self.assertTrue(ProposalChoice.objects.activated().count() == 1)
        pc3 = self.create_new_proposal_choice()
        self.assertTrue(ProposalChoice.objects.activated().count() == 2)
        # check on just one proposals
        self.assertTrue(self.proposal.proposalchoice_set.activated().count() == 2)
        # add a new proposal and add a choice to it
        p2 = Proposal.objects.create(proposal_name="Test Proposal 2", date_proposed=timezone.now(),
            proposal_description="This is a test proposal description", owned_by=self.user, proposal_group=None)
        pc4 = self.create_new_proposal_choice(proposal=p2)
        # one for main proposal
        self.assertTrue(self.proposal.proposalchoice_set.activated().count() == 2)
        # one for new proposal
        self.assertTrue(p2.proposalchoice_set.activated().count() == 1)
        # three in total
        self.assertTrue(ProposalChoice.objects.activated().count() == 3)
