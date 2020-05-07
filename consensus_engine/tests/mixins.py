from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User
from consensus_engine.models import Proposal, ProposalChoice, ChoiceTicket, ProposalGroup
from django.test import TestCase
from django.utils import timezone

class OneUserMixin(object):
    def setUp(self):
        # Every test needs access to the request factory.
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')


class TwoUserMixin(OneUserMixin):
    def setUp(self):
        # Every test needs access to the request factory.
        OneUserMixin.setUp(self)
        self.user2 = User.objects.create_user(
            username='jacob2', email='jacob@…', password='top_secret')



class ProposalGroupMixin(object):
    # needs to be used inconjunction with a UserMixin or it won't work

    def create_proposal_group(self, group_name="Test Group", owned_by=None,
        group_description="it's only a test group"):

        if owned_by == None:
            owned_by = self.user
        return ProposalGroup.objects.create(group_name=group_name, owned_by=owned_by,
            group_description=group_description)


class ProposalMixin(object):
    # needs to be used inconjunction with a UserMixin or it won't work

    def create_new_proposal(self, proposal_name="only a test", date_proposed=timezone.now(),
            proposal_description="yes, this is only a test", proposal_group=None, owned_by=None):
        if owned_by == None:
            owned_by = self.user
        return Proposal.objects.create(proposal_name=proposal_name, date_proposed=date_proposed,
            proposal_description=proposal_description, owned_by=owned_by, proposal_group=proposal_group)

    def create_proposal_with_two_proposal_choices(self, proposal_name="only a test", date_proposed=timezone.now(),
            proposal_description="yes, this is only a test", proposal_group=None,
            proposal_choice_1_name="Yes", proposal_choice_2_name="No"):
        p = self.create_new_proposal(proposal_name, date_proposed, proposal_description, proposal_group)
        pc1 = ProposalChoice.objects.create(proposal=p, text=proposal_choice_1_name,
            priority=100, activated_date=timezone.now())
        pc2 = ProposalChoice.objects.create(proposal=p, text=proposal_choice_2_name,
            priority=100, activated_date=timezone.now())
        return p
