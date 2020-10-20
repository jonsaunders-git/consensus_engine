from django.test import TestCase, RequestFactory
from .mixins import TwoUserMixin, ProposalGroupMixin, TemplateViewMixin
from consensus_engine.views import ProposalGroupMemberListView


class ProposalGroupMemberListViewTest(TwoUserMixin, TestCase,
                                      ProposalGroupMixin, TemplateViewMixin):
    view = ProposalGroupMemberListView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_list_new_group(self):
        pg, _ = self.create_proposal_group_with_test_proposal()
        context, _ = self.executeView(viewkwargs={'proposal_group_id': pg.id})
        self.assertTrue(context['members_list'].count() == 1)
        self.assertTrue(context['members_list'].first().user == self.user, context['members_list'].first().group == pg)

    def test_list_new_group_two_members(self):
        pg, _ = self.create_proposal_group_with_test_proposal()
        pg.join_group(self.user2)
        context, _ = self.executeView(viewkwargs={'proposal_group_id': pg.id})
        self.assertTrue(context['members_list'].count() == 2)
        self.assertTrue(context['members_list'].first().user == self.user,
                        context['members_list'].first().group == pg)
        self.assertTrue(context['members_list'].last().user == self.user2,
                        context['members_list'].last().group == pg)
        pg.remove_member(self.user2)
        self.assertTrue(context['members_list'].count() == 1)
        self.assertTrue(context['members_list'].first().user == self.user,
                        context['members_list'].first().group == pg)
