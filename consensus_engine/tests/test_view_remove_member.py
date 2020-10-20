from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import TwoUserMixin, ProposalGroupMixin, ViewMixin
from django.core.exceptions import PermissionDenied
from consensus_engine.views import RemoveGroupMemberView
from consensus_engine.models import GroupMembership


class RemoveGroupMemberViewTest(TwoUserMixin, TestCase,
                                ProposalGroupMixin, ViewMixin):
    path = '/proposals/1/choice/1/delete'
    view = RemoveGroupMemberView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def getSessionRequest(self, path=None):
        if path is None:
            path = self.path
        request = self.factory.get(path)
        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        request.user = self.user
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        return request

    def executeDeleteView(self, data, viewkwargs={}):
        request = self.getSessionRequest()
        v = self.get_view(kwargs=viewkwargs)

        _ = v.get_context_data(**viewkwargs)

        mutable = request.POST._mutable
        request.POST._mutable = True
        if 'okay_btn' in data:
            request.POST['okay_btn'] = 'okay_btn'
        else:
            request.POST['cancel_btn'] = 'cancel_btn'
        request.POST._mutable = mutable
        v.request = request

        v.object = viewkwargs['instance']
        self.assertTrue(v.delete(request))
        return request

    def test_remove_member(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        p.publish()
        pg.join_group(self.user2)
        gm = GroupMembership.objects.get(group=pg, user=self.user2)
        _ = self.executeDeleteView(data={'okay_btn'},
                                   viewkwargs={'pk': gm.id, 'instance': gm, 'proposal_group_id': pg.id})
        with self.assertRaises(GroupMembership.DoesNotExist):
            gm = GroupMembership.objects.get(pk=gm.id)

    def test_remove_member_cancel(self):
        pg, p = self.create_proposal_group_with_test_proposal()
        p.publish()
        pg.join_group(self.user2)
        gm = GroupMembership.objects.get(group=pg, user=self.user2)
        _ = self.executeDeleteView(data={},
                                   viewkwargs={'pk': gm.id, 'instance': gm, 'proposal_group_id': pg.id})
        gm = GroupMembership.objects.get(pk=gm.id)
        self.assertTrue(gm)

    def test_remove_member_permission_denied(self):
        pg, p = self.create_proposal_group_with_test_proposal(owned_by=self.user2)
        p.publish()
        gm = GroupMembership.objects.get(group=pg, user=self.user2)
        with self.assertRaises(PermissionDenied, msg="User management is only permitted for group owner."):
            _ = self.executeDeleteView(data={},
                                       viewkwargs={'pk': gm.id, 'instance': gm, 'proposal_group_id': pg.id})
