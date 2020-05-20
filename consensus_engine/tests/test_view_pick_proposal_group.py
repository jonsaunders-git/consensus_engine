from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import TwoUserMixin, ProposalGroupMixin, ViewMixin, ProposalMixin, TemplateViewMixin
from django.utils import timezone

from consensus_engine.views import PickProposalGroupView
from consensus_engine.models import ProposalGroup, Proposal

class PickProposalGroupViewTest(TwoUserMixin, TestCase,
                                ProposalGroupMixin, ProposalMixin, TemplateViewMixin):
    path = 'proposals/<int:proposal_id>/assign/group/'
    view = PickProposalGroupView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)


    def test_pick_proposal_no_proposal(self):
        pg = self.create_proposal_group()
        _ ,response = self.executeView(postargs={'proposal_group' : pg.id})
        self.assertTrue(
            response.url == '/consensus/proposalgroups/1/proposals/new/')

    def test_pick_proposal_with_proposal(self):
        pg = self.create_proposal_group()
        p = self.create_new_proposal()
        p_id = p.id
        self.assertFalse(p.proposal_group is not None)
        self.executeView(viewkwargs={'proposal_id' : p.id},
            postargs={'proposal_group' : pg.id})
        p.refresh_from_db()
        self.assertTrue(p.proposal_group is not None)
        self.assertTrue(p.proposal_group.id == pg.id)
        pg2 = self.create_proposal_group(group_name="test group 2")
        self.executeView(viewkwargs={'proposal_id' : p.id},
            postargs={'proposal_group' : pg2.id})
        p.refresh_from_db()
        self.assertTrue(p.proposal_group is not None)
        self.assertFalse(p.proposal_group.id == pg.id)
        self.assertTrue(p.proposal_group.id == pg2.id)

    def test_pick_proposal_with_not_owned(self):
        pg = self.create_proposal_group()
        p = self.create_new_proposal(owned_by=self.user2)
        p_id = p.id
        self.assertFalse(p.proposal_group is not None)
        c, _ = self.executeView(viewkwargs={'proposal_id' : p.id},
            postargs={'proposal_group' : pg.id})
        self.assertTrue(c['error_message'] == "You don't have permissions to edit the group.")
        p.refresh_from_db()
        self.assertTrue(p.proposal_group is None)

    def test_pick_proposal_with_invalid_proposal_group(self):
        self.assertTrue(ProposalGroup.objects.count() == 0)
        p = self.create_new_proposal()
        p_id = p.id
        self.assertFalse(p.proposal_group is not None)
        self.executeView(viewkwargs={'proposal_id' : p.id},
            postargs={'proposal_group' : 1})
        p.refresh_from_db()
        self.assertTrue(p.proposal_group is None)
