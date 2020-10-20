from django.test import TestCase, RequestFactory
from .mixins import TwoUserMixin, ProposalGroupMixin, ViewMixin
from consensus_engine.views import EditGroupMembershipView
from consensus_engine.models import ProposalGroup, GroupMembership
from django.core.exceptions import PermissionDenied


class EditGroupMembershipViewTest(TwoUserMixin, TestCase,
                                  ProposalGroupMixin, ViewMixin):
    path = '/proposalgroups/1/edit/'
    view = EditGroupMembershipView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_edit_group_membership(self):
        self.assertTrue(ProposalGroup.objects.count() == 0)
        pg = self.create_proposal_group()
        pg.join_group(self.user2, False)
        gm = GroupMembership.objects.get(user=self.user2, group=pg)
        self.assertFalse(gm.can_trial)
        _ = self.getValidView(data={'can_trial': True},
                              viewkwargs={'instance': gm})
        gm2 = GroupMembership.objects.get(user=self.user2, group=pg)
        self.assertTrue(gm2.can_trial)
        _ = self.getValidView(data={'can_trial': False},
                              viewkwargs={'instance': gm2})
        gm3 = GroupMembership.objects.get(user=self.user2, group=pg)
        self.assertFalse(gm3.can_trial)

    def test_edit_group_membership_no_permission(self):
        self.assertTrue(ProposalGroup.objects.count() == 0)
        pg = self.create_proposal_group(owned_by=self.user2)
        pg.join_group(self.user, False)
        gm = GroupMembership.objects.get(user=self.user2, group=pg)
        with self.assertRaises(PermissionDenied, msg="Editing is not allowed"):
            _ = self.getValidView(data={'can_trial': True},
                                  viewkwargs={'instance': gm})
