from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import OneUserMixin, ProposalGroupMixin, ViewMixin, ProposalMixin
from django.utils import timezone

from consensus_engine.views import PickProposalGroupView
from consensus_engine.models import ProposalGroup, Proposal

class PickProposalGroupViewTest(OneUserMixin, TestCase,
                                ProposalGroupMixin, ProposalMixin, ViewMixin):
    path = 'proposals/<int:proposal_id>/assign/group/'
    view = PickProposalGroupView

    def setUp(self):
        self.factory = RequestFactory()
        OneUserMixin.setUp(self)

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

    def executeTemplateView(self, viewkwargs={}, postargs={}):
        request = self.getSessionRequest()
        v = self.get_view(kwargs=viewkwargs)

        mutable = request.POST._mutable
        request.POST._mutable = True
        request.POST.update(postargs)
        request.POST._mutable = mutable
        v.request = request

        self.assertTrue(v.get_context_data(kwargs=viewkwargs))

        r = v.post(request, **viewkwargs)
        return r

    def test_pick_proposal_no_proposal(self):
        pg = self.create_proposal_group()
        response = self.executeTemplateView(postargs={'proposal_group' : pg.id})
        self.assertTrue(
            response.url == '/consensus/proposalgroups/1/proposals/new/')


    def test_pick_proposal_with_proposal(self):
        pg = self.create_proposal_group()
        p = self.create_new_proposal()
        p_id = p.id
        self.assertFalse(p.proposal_group is not None)
        response2 = self.executeTemplateView(viewkwargs={'proposal_id' : p.id},
            postargs={'proposal_group' : pg.id})
        p.refresh_from_db()
        self.assertTrue(p.proposal_group is not None)
        self.assertTrue(p.proposal_group.id == pg.id)
        pg2 = self.create_proposal_group(group_name="test group 2")
        response2 = self.executeTemplateView(viewkwargs={'proposal_id' : p.id},
            postargs={'proposal_group' : pg2.id})
        p.refresh_from_db()
        self.assertTrue(p.proposal_group is not None)
        self.assertFalse(p.proposal_group.id == pg.id)
        self.assertTrue(p.proposal_group.id == pg2.id)
