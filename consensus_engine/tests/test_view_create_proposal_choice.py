from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import TwoUserMixin, ProposalMixin, ViewMixin
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from consensus_engine.views import CreateProposalChoiceView
from consensus_engine.forms import ProposalChoiceForm
from consensus_engine.models import Proposal, ProposalChoice

class CreateProposalChoiceViewTest(TwoUserMixin, TestCase,
                                ProposalMixin, ViewMixin):
    path = '/proposals/1/choice/new/'
    form = ProposalChoiceForm
    view = CreateProposalChoiceView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_create_proposal_choice(self):
        dt = timezone.now()
        self.assertTrue(ProposalChoice.objects.filter(
            text = 'test choice').count() == 0)
        p = self.create_new_proposal()
        self.assertTrue(p.proposalchoice_set.count() == 0)
        # create choice
        request = self.getValidView(data={'text': 'test choice',
                'priority': '100'}, viewkwargs={'proposal_id' : p.id})
        self.assertTrue(ProposalChoice.objects.filter(
            text = 'test choice').count() == 1)
        self.assertTrue(p.proposalchoice_set.count() == 1)
        pc = p.proposalchoice_set.first()
        self.assertTrue(pc.text == 'test choice')
        self.assertTrue(pc.priority == 100)
        self.assertTrue(pc.activated_date >= dt
                            and pc.activated_date <= timezone.now())
        self.assertTrue(pc.deactivated_date is None)
        request = self.getValidView(data={'text': 'test choice 2',
                'priority': '200'}, viewkwargs={'proposal_id' : p.id})
        self.assertTrue(p.proposalchoice_set.count() == 2)
        self.assertTrue(p.proposalchoice_set.first() == pc)
        pc2 = p.proposalchoice_set.last()
        self.assertTrue(pc.text == 'test choice')
        self.assertTrue(pc.priority == 100)
        self.assertTrue(pc.activated_date >= dt
                            and pc.activated_date <= timezone.now())
        self.assertTrue(pc2.deactivated_date is None)
        self.assertTrue(pc2.text == 'test choice 2')
        self.assertTrue(pc2.priority == 200)
        self.assertTrue(pc2.activated_date >= dt
                            and pc2.activated_date <= timezone.now())
        self.assertTrue(pc2.deactivated_date is None)

    def test_create_proposal_choice_permission_denied(self):
        dt = timezone.now()
        self.assertTrue(ProposalChoice.objects.filter(
            text = 'test choice').count() == 0)
        p = self.create_new_proposal(owned_by=self.user2)
        self.assertTrue(p.proposalchoice_set.count() == 0)
        # create choice
        with self.assertRaises(PermissionDenied) as e:
            request = self.getValidView(data={'text': 'test choice',
                    'priority': '100'}, viewkwargs={'proposal_id' : p.id})
