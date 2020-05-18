from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import OneUserMixin, ProposalGroupMixin, ViewMixin, ProposalMixin
from django.utils import timezone

from consensus_engine.views import EditProposalView
from consensus_engine.forms import ProposalForm
from consensus_engine.models import Proposal

class EditProposalViewTest(OneUserMixin, TestCase,
                                ProposalMixin, ViewMixin):
    path = '/proposals/new/'
    form = ProposalForm
    view = EditProposalView

    def setUp(self):
        self.factory = RequestFactory()
        OneUserMixin.setUp(self)

    def test_edit_proposal(self):
        dt = timezone.now()
        self.assertTrue(Proposal.objects.filter(
            proposal_name = 'test proposal').count() == 0)
        p = self.create_new_proposal()
        original_description = p.proposal_description
        request = self.getValidView(
                    data={'proposal_name' : 'updated test proposal',
                            'proposal_description' : original_description},
                    viewkwargs={'instance' : p})
        q = Proposal.objects.filter(proposal_name = 'test proposal')
        self.assertTrue(q.count() == 0)
        q2 = Proposal.objects.filter(proposal_name = 'updated test proposal')
        self.assertTrue(q2.count() == 1)
        p2 = q2.first()
        self.assertTrue(p == p2)
        q3 = Proposal.objects.filter(proposal_description = original_description)
        self.assertTrue(q3.count() == 1)
        request = self.getValidView(
                    data={'proposal_name' : p.proposal_name,
                            'proposal_description' : 'updated test description'},
                    viewkwargs={'instance' : p})
        q4 = Proposal.objects.filter(proposal_description = original_description)
        self.assertTrue(q4.count() == 0)
        q5 = Proposal.objects.filter(proposal_description = 'updated test description')
        self.assertTrue(q5.count() == 1)
