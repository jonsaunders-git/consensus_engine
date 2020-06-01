from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import OneUserMixin, ProposalGroupMixin, ViewMixin
from django.utils import timezone

from consensus_engine.views import CreateProposalGroupView
from consensus_engine.forms import ProposalGroupForm
from consensus_engine.models import ProposalGroup, GroupMembership

class CreateProposalViewTest(OneUserMixin, TestCase,
                                ProposalGroupMixin, ViewMixin):
    path = '/proposalgroups/new/'
    form = ProposalGroupForm
    view = CreateProposalGroupView

    def setUp(self):
        self.factory = RequestFactory()
        OneUserMixin.setUp(self)

    def test_create_proposal_group(self):
        dt = timezone.now()
        self.assertTrue(ProposalGroup.objects.count() == 0)
        request = self.getValidView({'group_name' : 'test group', 'group_description' : 'test group description'})
        q = ProposalGroup.objects.filter(group_name = 'test group')
        self.assertTrue(q.count() == 1)
        p = q.first()
        self.assertTrue(p.group_description == 'test group description')
        self.assertTrue(p.owned_by == self.user)
        gm = GroupMembership.objects.filter(user=self.user, group=p)
        self.assertTrue(gm.count()==1)
        self.assertTrue(gm.first().date_joined >= dt and gm.first().date_joined <= timezone.now())
