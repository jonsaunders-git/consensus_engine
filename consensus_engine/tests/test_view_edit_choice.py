from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import TwoUserMixin, ProposalGroupMixin, ViewMixin, ProposalMixin
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from consensus_engine.views import EditProposalChoiceView
from consensus_engine.forms import ProposalChoiceForm
from consensus_engine.models import Proposal, ProposalChoice

class EditProposalChoicdeViewTest(TwoUserMixin, TestCase,
                                ProposalMixin, ViewMixin):
    path = '/proposals/1/choice/2/'
    form = ProposalChoiceForm
    view = EditProposalChoiceView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_edit_choice(self):
        dt = timezone.now()
        p = self.create_proposal_with_two_proposal_choices()
        pc1 = p.proposalchoice_set.first()
        pc2 = p.proposalchoice_set.last()
        self.assertFalse(pc1.text == 'Yes')
        self.assertTrue(pc1.priority == 100)
        self.assertTrue(pc2.text == 'No')
        self.assertTrue(pc2.priority == 200)
        original_priority = pc1.priority
        request = self.getValidView(
                    data={'text' : 'updated Yes',
                            'priority' : original_priority},
                    viewkwargs={'instance' : pc1, 'proposal_id' : p.id})
        self.assertTrue(pc1.text == 'updated Yes')
        self.assertTrue(pc1.priority == original_priority)
        self.assertTrue(pc2.text == 'No')
        self.assertTrue(pc2.priority == 200)
        request = self.getValidView(
                    data={'text' : pc1.text,
                            'priority' : '200'},
                    viewkwargs={'instance' : pc1, 'proposal_id' : p.id})
        self.assertTrue(pc1.text == 'updated Yes')
        self.assertTrue(pc1.priority == 200)
        request = self.getValidView(
                    data={'text' : 'updated No',
                            'priority' : '300'},
                    viewkwargs={'instance' : pc2, 'proposal_id' : p.id})
        self.assertTrue(pc1.text == 'updated Yes')
        self.assertTrue(pc1.priority == 200)
        self.assertTrue(pc2.text == 'updated No')
        self.assertTrue(pc2.priority == 300)


    def test_edit_choice_permission_denied(self):
        dt = timezone.now()
        p = self.create_proposal_with_two_proposal_choices(owned_by=self.user2)
        pc1 = p.proposalchoice_set.first()
        pc2 = p.proposalchoice_set.last()
        original_priority = pc1.priority
        with self.assertRaises(PermissionDenied) as e:
            request = self.getValidView(
                        data={'text' : 'updated Yes',
                                'priority' : original_priority},
                                viewkwargs={'instance' : pc1, 'proposal_id' : p.id})
