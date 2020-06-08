from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import TwoUserMixin, ProposalGroupMixin, ViewMixin, ProposalMixin
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from consensus_engine.views import DeleteProposalChoiceView
from consensus_engine.models import Proposal, ProposalChoice

class EditProposalChoicdeViewTest(TwoUserMixin, TestCase,
                                ProposalMixin, ViewMixin):
    path = '/proposals/1/choice/1/delete'
    view = DeleteProposalChoiceView

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

        c = v.get_context_data(kwargs=viewkwargs)
        self.assertTrue(c['proposal'] is not None)

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

    def test_edit_choice(self):
        p = self.create_proposal_with_two_proposal_choices()
        pc1 = p.proposalchoice_set.first()
        self.assertTrue(pc1.deactivated_date is None)
        request = self.executeDeleteView(
                    data={'okay_btn'},
                    viewkwargs={'pk' : pc1.id, 'instance' : pc1, 'proposal_id' : p.id})
        pc1 = ProposalChoice.objects.get(pk=pc1.id)
        self.assertTrue(pc1.deactivated_date is not None)

    def test_edit_choice_cancel(self):
        dt = timezone.now()
        p = self.create_proposal_with_two_proposal_choices()
        pc1 = p.proposalchoice_set.first()
        self.assertTrue(pc1.deactivated_date is None)
        request = self.executeDeleteView(
                    data={},
                    viewkwargs={'pk' : pc1.id, 'instance' : pc1, 'proposal_id' : p.id})
        pc1 = ProposalChoice.objects.get(pk=pc1.id)
        self.assertTrue(pc1.deactivated_date is None)

    def test_edit_choice_permission_denied(self):
        p = self.create_proposal_with_two_proposal_choices(owned_by=self.user2)
        pc1 = p.proposalchoice_set.first()
        self.assertTrue(pc1.deactivated_date is None)
        with self.assertRaises(PermissionDenied) as e:
            request = self.executeDeleteView(
                    data={'okay_btn'},
                    viewkwargs={'pk' : pc1.id, 'instance' : pc1, 'proposal_id' : p.id})
