from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import OneUserMixin, ProposalGroupMixin, ViewMixin
from django.utils import timezone

from consensus_engine.views import CreateProposalGroupView
from consensus_engine.forms import ProposalGroupForm
from consensus_engine.models import ProposalGroup

class CreateProposalViewTest(OneUserMixin, TestCase,
                                ProposalGroupMixin, ViewMixin):
    path = '/proposalgroups/new/'
    form = ProposalGroupForm
    view = CreateProposalGroupView

    def setUp(self):
        self.factory = RequestFactory()
        OneUserMixin.setUp(self)

    def test_create_proposal(self):
        self.assertTrue(ProposalGroup.objects.count() == 0)
        request = self.getValidView({'group_name' : 'test group', 'group_description' : 'test group description'})
        q = ProposalGroup.objects.filter(group_name = 'test group')
        self.assertTrue(q.count() == 1)
        p = q.first()
        self.assertTrue(p.group_description == 'test group description')
        self.assertTrue(p.owned_by == self.user)
