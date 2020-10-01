from django.test import TestCase, RequestFactory
from .mixins import TwoUserMixin, ProposalGroupMixin, ViewMixin
from django.utils import timezone

from consensus_engine.views import CreateProposalView
from consensus_engine.forms import ProposalForm
from consensus_engine.models import Proposal
from django.core.exceptions import PermissionDenied


class CreateProposalViewTest(TwoUserMixin, TestCase,
                             ProposalGroupMixin, ViewMixin):
    path = '/proposals/new/'
    form = ProposalForm
    view = CreateProposalView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_create_proposal(self):
        dt = timezone.now()
        self.assertTrue(Proposal.objects.filter(
            proposal_name='test proposal').count() == 0)
        self.getValidView({'proposal_name': 'test proposal',
                           'proposal_description': 'test description'}, postargs={'options': '0'})
        q = Proposal.objects.filter(proposal_name='test proposal')
        self.assertTrue(q.count() == 1)
        p = q.first()
        self.assertTrue(p.proposal_description == 'test description')
        self.assertTrue(p.date_proposed <= timezone.now()
                        and p.date_proposed >= dt)
        self.assertTrue(p.owned_by == self.user)
        self.assertTrue(p.proposal_group is None)

    def test_create_proposal_within_group(self):
        pg = self.create_proposal_group()
        dt = timezone.now()
        self.assertTrue(Proposal.objects.filter(
                            proposal_name='test proposal').count() == 0)
        self.getValidView(data={'proposal_name': 'test proposal',
                          'proposal_description': 'test description'},
                          viewkwargs={'proposal_group_id': pg.id}, postargs={'options': '0'})
        q = Proposal.objects.filter(proposal_name='test proposal')
        self.assertTrue(q.count() == 1)
        p = q.first()
        self.assertTrue(p.proposal_description == 'test description')
        self.assertTrue(p.date_proposed <= timezone.now()
                        and p.date_proposed >= dt)
        self.assertTrue(p.owned_by == self.user)
        self.assertTrue(p.proposal_group == pg)

    def test_create_proposal_within_group_not_member(self):
        pg = self.create_proposal_group(owned_by=self.user2)
        self.assertTrue(Proposal.objects.filter(
                            proposal_name='test proposal').count() == 0)
        with self.assertRaises(PermissionDenied,
                               msg="Adding a Proposal to a group you are not a member of is not allowed"):
            self.getValidView(data={'proposal_name': 'test proposal',
                              'proposal_description': 'test description'},
                              viewkwargs={'proposal_group_id': pg.id}, postargs={'options': '0'})
