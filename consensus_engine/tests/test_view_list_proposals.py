from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import TwoUserMixin, ProposalGroupMixin, ViewMixin, ProposalMixin, TemplateViewMixin
from django.utils import timezone

from consensus_engine.views import ProposalListView, ProposalListGroupView
from consensus_engine.models import ProposalGroup, Proposal

class ProposalListViewTest(TwoUserMixin, TestCase,
                                ProposalGroupMixin, ProposalMixin, TemplateViewMixin):
    view = ProposalListView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_list_proposals_no_proposals(self):
        context , _ = self.executeView()
        self.assertTrue(context['proposals_list'].count() == 0)

    def test_list_proposals_some_proposals(self):
        p = self.create_new_proposal()
        context , _ = self.executeView()
        self.assertTrue(context['proposals_list'].count() == 1)
        self.assertTrue( context['proposals_list'].first()['id'] == p.id)
        p2 = self.create_new_proposal()
        context2 , _ = self.executeView()
        self.assertTrue(context2['proposals_list'].count() == 2)
        self.assertTrue(context2['proposals_list'].filter(id=p.id).count() == 1)
        self.assertTrue(context2['proposals_list'].filter(id=p2.id).count() == 1)
        self.assertTrue(context2['proposals_list'].filter(id=99).count() == 0)
        # create a proposal by another user
        p3 = self.create_new_proposal(owned_by = self.user2)
        context3 , _ = self.executeView()
        self.assertTrue(context3['proposals_list'].count() == 2)
        self.assertTrue(context3['proposals_list'].filter(id=p.id).count() == 1)
        self.assertTrue(context3['proposals_list'].filter(id=p2.id).count() == 1)
        # switch user
        self.current_user = self.user2
        context4 , _ = self.executeView()
        self.assertTrue(context4['proposals_list'].count() == 1)
        self.assertTrue(context4['proposals_list'].filter(id=p3.id).count() == 1)
        self.assertTrue(context4['proposals_list'].filter(id=p.id).count() == 0)



class ProposalListGroupViewTest(TwoUserMixin, TestCase,
                                ProposalGroupMixin, ProposalMixin, TemplateViewMixin):
    view = ProposalListGroupView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_list_proposals_no_proposals_in_group(self):
        pg = self.create_proposal_group()
        context , _ = self.executeView(viewkwargs={'proposal_group_id' : pg.id})
        self.assertTrue(context['proposals_list'].count() == 0)

    def test_list_proposals_some_proposals_in_group(self):
        pg = self.create_proposal_group()
        p = self.create_new_proposal(proposal_group = pg)
        context , _ = self.executeView(viewkwargs={'proposal_group_id' : pg.id})
        self.assertTrue(context['proposals_list'].count() == 1)
        self.assertTrue( context['proposals_list'].first()['id'] == p.id)
        p2 = self.create_new_proposal(proposal_group = pg)
        context2 , _ = self.executeView(viewkwargs={'proposal_group_id' : pg.id})
        self.assertTrue(context2['proposals_list'].count() == 2)
        self.assertTrue(context2['proposals_list'].filter(id=p.id).count() == 1)
        self.assertTrue(context2['proposals_list'].filter(id=p2.id).count() == 1)
        self.assertTrue(context2['proposals_list'].filter(id=99).count() == 0)
        # create another proposal group and add a proposal to that
        pg2 = self.create_proposal_group()
        p3 = self.create_new_proposal(proposal_group = pg2)
        context3 , _ = self.executeView(viewkwargs={'proposal_group_id' : pg2.id})
        self.assertTrue(context3['proposals_list'].count() == 1)
        self.assertTrue(context3['proposals_list'].first()['id'] == p3.id)
        context4 , _ = self.executeView(viewkwargs={'proposal_group_id' : pg.id})
        self.assertTrue(context2['proposals_list'].count() == 2)
