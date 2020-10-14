from django.test import TestCase, RequestFactory
from .mixins import TwoUserMixin, ProposalGroupMixin, ProposalMixin, TemplateViewMixin
from consensus_engine.views import ProposalListView, ProposalListGroupView


class ProposalListViewTest(TwoUserMixin, TestCase,
                           ProposalGroupMixin, ProposalMixin, TemplateViewMixin):
    view = ProposalListView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_list_proposals_no_proposals(self):
        context, _ = self.executeView()
        self.assertTrue(context['draft_proposals_list'].count() == 0)

    def test_list_proposals_some_proposals(self):
        p = self.create_new_proposal()
        context, _ = self.executeView()
        self.assertTrue(context['draft_proposals_list'].count() == 1)
        self.assertTrue(context['draft_proposals_list'].first()['id'] == p.id)
        self.assertTrue(context['trial_proposals_list'].count() == 0)
        self.assertTrue(context['published_proposals_list'].count() == 0)
        self.assertTrue(context['on_hold_proposals_list'].count() == 0)
        self.assertTrue(context['archived_proposals_list'].count() == 0)
        p2 = self.create_new_proposal()
        context2, _ = self.executeView()
        self.assertTrue(context2['draft_proposals_list'].count() == 2)
        self.assertTrue(context2['draft_proposals_list'].filter(id=p.id).count() == 1)
        self.assertTrue(context2['draft_proposals_list'].filter(id=p2.id).count() == 1)
        self.assertTrue(context2['draft_proposals_list'].filter(id=99).count() == 0)
        self.assertTrue(context['trial_proposals_list'].count() == 0)
        self.assertTrue(context['published_proposals_list'].count() == 0)
        self.assertTrue(context['on_hold_proposals_list'].count() == 0)
        self.assertTrue(context['archived_proposals_list'].count() == 0)
        # create a proposal by another user
        p3 = self.create_new_proposal(owned_by=self.user2)
        context3, _ = self.executeView()
        self.assertTrue(context3['draft_proposals_list'].count() == 2)
        self.assertTrue(context3['draft_proposals_list'].filter(id=p.id).count() == 1)
        self.assertTrue(context3['draft_proposals_list'].filter(id=p2.id).count() == 1)
        self.assertTrue(context['trial_proposals_list'].count() == 0)
        self.assertTrue(context['published_proposals_list'].count() == 0)
        self.assertTrue(context['on_hold_proposals_list'].count() == 0)
        self.assertTrue(context['archived_proposals_list'].count() == 0)
        # switch user
        self.current_user = self.user2
        context4, _ = self.executeView()
        self.assertTrue(context4['draft_proposals_list'].count() == 1)
        self.assertTrue(context4['draft_proposals_list'].filter(id=p3.id).count() == 1)
        self.assertTrue(context4['draft_proposals_list'].filter(id=p.id).count() == 0)
        self.assertTrue(context['trial_proposals_list'].count() == 0)
        self.assertTrue(context['published_proposals_list'].count() == 0)
        self.assertTrue(context['on_hold_proposals_list'].count() == 0)
        self.assertTrue(context['archived_proposals_list'].count() == 0)


class ProposalListGroupViewTest(TwoUserMixin, TestCase,
                                ProposalGroupMixin, ProposalMixin, TemplateViewMixin):
    view = ProposalListGroupView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_list_proposals_no_proposals_in_group(self):
        pg = self.create_proposal_group()
        context, _ = self.executeView(viewkwargs={'proposal_group_id': pg.id})
        self.assertTrue(context['proposals_list'].count() == 0)

    def test_list_proposals_some_proposals_in_group(self):
        pg = self.create_proposal_group()
        p = self.create_new_proposal(proposal_group=pg)
        p.publish()
        context, _ = self.executeView(viewkwargs={'proposal_group_id': pg.id})
        self.assertTrue(context['proposals_list'].count() == 1)
        self.assertTrue(context['proposals_list'].first()['id'] == p.id)
        p2 = self.create_new_proposal(proposal_group=pg)
        p2.publish()
        context2, _ = self.executeView(viewkwargs={'proposal_group_id': pg.id})
        self.assertTrue(context2['proposals_list'].count() == 2)
        self.assertTrue(context2['proposals_list'].filter(id=p.id).count() == 1)
        self.assertTrue(context2['proposals_list'].filter(id=p2.id).count() == 1)
        self.assertTrue(context2['proposals_list'].filter(id=99).count() == 0)
        # create another proposal group and add a proposal to that
        pg2 = self.create_proposal_group()
        p3 = self.create_new_proposal(proposal_group=pg2)
        p3.publish()
        context3, _ = self.executeView(viewkwargs={'proposal_group_id': pg2.id})
        self.assertTrue(context3['proposals_list'].count() == 1)
        self.assertTrue(context3['proposals_list'].first()['id'] == p3.id)
        self.executeView(viewkwargs={'proposal_group_id': pg.id})
        self.assertTrue(context2['proposals_list'].count() == 2)

    def test_list_proposals_with_states(self):
        pg = self.create_proposal_group()
        p = self.create_new_proposal(proposal_group=pg)
        context, _ = self.executeView(viewkwargs={'proposal_group_id': pg.id})
        self.assertTrue(context['proposals_list'].count() == 0)
        p.trial()
        context, _ = self.executeView(viewkwargs={'proposal_group_id': pg.id})
        self.assertTrue(context['proposals_list'].count() == 1)
        p.publish()
        context, _ = self.executeView(viewkwargs={'proposal_group_id': pg.id})
        self.assertTrue(context['proposals_list'].count() == 1)
        p.hold()
        context, _ = self.executeView(viewkwargs={'proposal_group_id': pg.id})
        self.assertTrue(context['proposals_list'].count() == 0)
        p.archive()
        context, _ = self.executeView(viewkwargs={'proposal_group_id': pg.id})
        self.assertTrue(context['proposals_list'].count() == 0)
