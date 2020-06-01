from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import TwoUserMixin, ProposalGroupMixin, ViewMixin, ProposalMixin, TemplateViewMixin
from django.utils import timezone

from consensus_engine.views import JoinProposalGroupMembersView
from consensus_engine.models import ProposalGroup, Proposal, ChoiceTicket
from django.db import DataError



class JoinProposalGroupMembersViewTest(TwoUserMixin, TestCase,
                                ProposalGroupMixin, ProposalMixin, TemplateViewMixin):
    view = JoinProposalGroupMembersView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_join_group(self):
        pg = self.create_proposal_group(owned_by=self.user2)
        # check that total votes = 0 if there are no votes
        context , _ = self.executeView(viewkwargs={'proposal_group_id' : pg.id})
        self.assertTrue(context['proposalgroup'].id == pg.id)
        l2 = ProposalGroup.objects.list_of_membership(self.user2)
        self.assertTrue(pg.id in l2)
        self.assertTrue(ProposalGroup.objects.groups_for_member(self.user2).count()==1)
        self.assertTrue(ProposalGroup.objects.groups_for_member(self.user).count()==1)
        with self.assertRaises(DataError) as e:
            context , _ = self.executeView(viewkwargs={'proposal_group_id' : pg.id})
