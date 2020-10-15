from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import TwoUserMixin, ProposalGroupMixin, ViewMixin, ProposalMixin, TemplateViewMixin
from consensus_engine.views import InvitesView, InviteView, InvitePersonView
from consensus_engine.models import GroupInvite


class InvitesViewTest(TwoUserMixin, TestCase,
                      ProposalGroupMixin, ProposalMixin, TemplateViewMixin):
    view = InvitesView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_invites(self):
        context , _ = self.executeView()
        self.assertTrue(context['invites_list'].count() == 0)

    def test_list_votes_some_votes(self):
        pg = self.create_proposal_group(owned_by=self.user2)
        i = pg.invite_user(self.user2, self.user)
        context , _ = self.executeView()
        self.assertTrue(context['invites_list'].count() == 1)
        pg2 = self.create_proposal_group(owned_by=self.user2)
        i2 = pg2.invite_user(self.user2, self.user)
        self.assertTrue(context['invites_list'].count() == 2)
        i.accept()
        self.assertTrue(context['invites_list'].count() == 1)
        self.assertTrue(pg.is_user_member(self.user))
        i2.decline()
        self.assertTrue(context['invites_list'].count() == 0)
        self.assertFalse(pg2.is_user_member(self.user))
        pg3 = self.create_proposal_group(owned_by=self.user2)
        i3 = pg3.invite_user(self.user2, self.user)
        self.assertTrue(context['invites_list'].count() == 1)


class InviteViewTest(TwoUserMixin, TestCase,
                     ProposalGroupMixin, ViewMixin):
    path = '/'
    view = InviteView

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

    def executeAcceptView(self, data, viewkwargs={}):
        request = self.getSessionRequest()
        v = self.get_view(kwargs=viewkwargs)
        c = v.get_context_data(**viewkwargs)
        self.assertTrue(c['invite'] is not None)
        mutable = request.POST._mutable
        request.POST._mutable = True
        if 'accept_btn' in data:
            request.POST['accept_btn'] = 'accept_btn'
        else:
            request.POST['decline_btn'] = 'decline_btn'
        request.POST._mutable = mutable
        v.request = request
        v.post(request, **viewkwargs)
        return request

    def test_accept_invite(self):
        pg = self.create_proposal_group(owned_by=self.user2)
        i = pg.invite_user(self.user2, self.user)
        self.assertTrue(pg.has_user_been_invited(self.user))
        _ = self.executeAcceptView(
                    data={'accept_btn'},
                    viewkwargs={'invite_id': i.id})
        self.assertFalse(pg.has_user_been_invited(self.user))
        self.assertTrue(pg.is_user_member(self.user))

    def test_decline_invite(self):
        pg = self.create_proposal_group(owned_by=self.user2)
        i = pg.invite_user(self.user2, self.user)
        self.assertTrue(pg.has_user_been_invited(self.user))
        _ = self.executeAcceptView(
                    data={'decline_btn'},
                    viewkwargs={'invite_id': i.id})
        self.assertFalse(pg.has_user_been_invited(self.user))
        self.assertFalse(pg.is_user_member(self.user))


class InvitePersonViewTest(TwoUserMixin, TestCase,
                           ProposalGroupMixin, ViewMixin):
    path = '/'
    view = InvitePersonView

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

    def executeAcceptView(self, data, viewkwargs={}):
        request = self.getSessionRequest()
        v = self.get_view(kwargs=viewkwargs)
        c = v.get_context_data(**viewkwargs)
        self.assertTrue(c['group'] is not None)
        mutable = request.POST._mutable
        request.POST._mutable = True
        if 'user_id' in data:
            request.POST['user_id'] = data['user_id']
        request.POST._mutable = mutable
        v.request = request
        v.post(request, **viewkwargs)
        return request

    def test_invite_person(self):
        pg = self.create_proposal_group()
        _ = self.executeAcceptView(
                    data={'user_id': self.user2.id},
                    viewkwargs={'pk': pg.id})
        self.assertTrue(pg.has_user_been_invited(self.user2))

    def test_invite_person_already_a_member(self):
        pg = self.create_proposal_group()
        pg.join_group(self.user2)
        _ = self.executeAcceptView(
                    data={'user_id': self.user2.id},
                    viewkwargs={'pk': pg.id})
        self.assertFalse(pg.has_user_been_invited(self.user2))

    def test_invite_person_already_invited(self):
        pg = self.create_proposal_group()
        pg.invite_user(self.user, self.user2)
        _ = self.executeAcceptView(
                    data={'user_id': self.user2.id},
                    viewkwargs={'pk': pg.id})
        self.assertTrue(GroupInvite.objects.my_open_invites_count(self.user2) == 1)
