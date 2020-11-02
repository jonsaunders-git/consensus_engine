from django.test import TestCase, RequestFactory
from .mixins import TwoUserMixin, ProposalGroupMixin, ProposalMixin, TemplateViewMixin
from consensus_engine.views import ProposalGroupListView, MyProposalGroupListView


class ProposalGroupListViewTest(TwoUserMixin, TestCase,
                                ProposalGroupMixin, ProposalMixin, TemplateViewMixin):
    view = ProposalGroupListView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_list_proposals_no_proposals(self):
        context, _ = self.executeView()
        self.assertTrue(context['proposalgroup_list'].count() == 0)

    def test_list_proposals_some_proposals(self):
        pg = self.create_proposal_group()
        context, _ = self.executeView()
        self.assertTrue(context['proposalgroup_list'].count() == 1)
        self.assertTrue(context['proposalgroup_list'].first().id == pg.id)
        pg2 = self.create_proposal_group()
        context2, _ = self.executeView()
        self.assertTrue(context2['proposalgroup_list'].count() == 2)
        self.assertTrue(context2['proposalgroup_list'].filter(id=pg.id).count() == 1)
        self.assertTrue(context2['proposalgroup_list'].filter(id=pg2.id).count() == 1)
        self.assertTrue(context2['proposalgroup_list'].filter(id=99).count() == 0)
        # create a proposal by another user
        pg3 = self.create_proposal_group(owned_by=self.user2)
        context3, _ = self.executeView()
        self.assertTrue(context3['proposalgroup_list'].count() == 3)
        self.assertTrue(context3['proposalgroup_list'].filter(id=pg.id).count() == 1)
        self.assertTrue(context3['proposalgroup_list'].filter(id=pg2.id).count() == 1)
        self.assertTrue(context3['proposalgroup_list'].filter(id=pg3.id).count() == 1)


class MyProposalGroupListViewTest(TwoUserMixin, TestCase,
                                  ProposalGroupMixin, ProposalMixin, TemplateViewMixin):
    view = MyProposalGroupListView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_list_proposals_no_proposals(self):
        context, _ = self.executeView()
        self.assertTrue(context['proposalgroup_list'].count() == 0)

    def test_list_proposals_some_proposals(self):
        pg = self.create_proposal_group()
        context, _ = self.executeView()
        self.assertTrue(context['proposalgroup_list'].count() == 1)
        self.assertTrue(context['proposalgroup_list'].first().id == pg.id)
        pg2 = self.create_proposal_group()
        context2, _ = self.executeView()
        self.assertTrue(context2['proposalgroup_list'].count() == 2)
        self.assertTrue(context2['proposalgroup_list'].filter(id=pg.id).count() == 1)
        self.assertTrue(context2['proposalgroup_list'].filter(id=pg2.id).count() == 1)
        self.assertTrue(context2['proposalgroup_list'].filter(id=99).count() == 0)
        # create a proposal by another user
        pg3 = self.create_proposal_group(owned_by=self.user2)
        context3, _ = self.executeView()
        self.assertTrue(context3['proposalgroup_list'].count() == 2)
        self.assertTrue(context3['proposalgroup_list'].filter(id=pg3.id).count() == 0)
        # switch user
        self.current_user = self.user2
        context4, _ = self.executeView()
        self.assertTrue(context4['proposalgroup_list'].count() == 1)
        self.assertTrue(context4['proposalgroup_list'].filter(id=pg3.id).count() == 1)
        self.assertTrue(context4['proposalgroup_list'].filter(id=pg.id).count() == 0)
