from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import OneUserMixin, ProposalGroupMixin, ViewMixin, ProposalMixin
from django.utils import timezone

from consensus_engine.views import EditProposalGroupView
from consensus_engine.forms import ProposalGroupForm
from consensus_engine.models import ProposalGroup

class EditProposalGroupViewTest(OneUserMixin, TestCase,
                                ProposalGroupMixin, ViewMixin):
    path = '/proposalgroups/1/edit/'
    form = ProposalGroupForm
    view = EditProposalGroupView

    def setUp(self):
        self.factory = RequestFactory()
        OneUserMixin.setUp(self)

    def test_edit_proposal(self):
        dt = timezone.now()
        self.assertTrue(ProposalGroup.objects.count() == 0)
        pg = self.create_proposal_group()
        self.assertTrue(ProposalGroup.objects.filter(group_name = 'test group').count() == 1)
        original_description = pg.group_description
        request = self.getValidView(
                    data={'group_name' : 'updated test group',
                            'group_description' : original_description},
                    viewkwargs={'instance' : pg})
        q = ProposalGroup.objects.filter(group_name = 'test group')
        self.assertTrue(q.count() == 0)
        q2 = ProposalGroup.objects.filter(group_name = 'updated test group')
        self.assertTrue(q2.count() == 1)
        pg2 = q2.first()
        self.assertTrue(pg == pg2)
        q3 = ProposalGroup.objects.filter(group_description = original_description)
        self.assertTrue(q3.count() == 1)
        request = self.getValidView(
                    data={'group_name' : pg.group_name,
                            'group_description' : 'updated test description'},
                    viewkwargs={'instance' : pg})
        q4 = ProposalGroup.objects.filter(group_description = original_description)
        self.assertTrue(q4.count() == 0)
        q5 = ProposalGroup.objects.filter(group_description = 'updated test description')
        self.assertTrue(q5.count() == 1)
