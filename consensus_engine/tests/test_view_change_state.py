from django.test import TestCase, RequestFactory
from .mixins import OneUserMixin, ProposalMixin, TemplateViewMixin

from consensus_engine.views import StateView, StateChangeConfirmationView
from consensus_engine.utils import ProposalState


class StateViewTest(OneUserMixin, TestCase,
                    ProposalMixin, TemplateViewMixin):
    view = StateView

    def setUp(self):
        self.factory = RequestFactory()
        OneUserMixin.setUp(self)

    def test_change_state(self):
        p = self.create_new_proposal()
        self.assertTrue(p.current_state == ProposalState.DRAFT)
        _, post_request = self.executeView(viewkwargs={'proposal_id': p.id}, postargs={'state': '1'})
        p.trial()
        p.refresh_from_db()
        self.assertTrue(post_request.url == '/consensus/proposals/1/confirm_change_state/1')
        _, post_request = self.executeView(viewkwargs={'proposal_id': p.id}, postargs={'state': '2'})
        p.publish()
        p.refresh_from_db()
        self.assertTrue(post_request.url == '/consensus/proposals/1/confirm_change_state/2')
        _, post_request = self.executeView(viewkwargs={'proposal_id': p.id}, postargs={'state': '3'})
        p.hold()
        p.refresh_from_db()
        self.assertTrue(post_request.url == '/consensus/proposals/1/confirm_change_state/3')
        _, post_request = self.executeView(viewkwargs={'proposal_id': p.id}, postargs={'state': '4'})
        p.archive()
        p.refresh_from_db()
        self.assertTrue(post_request.url == '/consensus/proposals/1/confirm_change_state/4')

    def test_key_error(self):
        p = self.create_new_proposal()
        self.assertTrue(p.current_state == ProposalState.DRAFT)
        _, response = self.executeView(viewkwargs={'proposal_id': p.id}, postargs={})
        content = str(response.content)
        self.assertTrue(content.find("You didn&#x27;t select a state.") > 0)


class StateChangeConfirmationViewTest(OneUserMixin, TestCase,
                                      ProposalMixin, TemplateViewMixin):
    view = StateChangeConfirmationView

    def setUp(self):
        self.factory = RequestFactory()
        OneUserMixin.setUp(self)

    def test_confirm_change_state(self):
        p = self.create_new_proposal()
        self.assertTrue(p.current_state == ProposalState.DRAFT)
        _, post_request = self.executeView(viewkwargs={'proposal_id': p.id, 'current_state': p.current_state,
                                                       'next_state': ProposalState.TRIAL}, postargs={'state': '1'})
        p.refresh_from_db()
        self.assertTrue(p.current_state == ProposalState.TRIAL)
        _, post_request = self.executeView(viewkwargs={'proposal_id': p.id, 'current_state': p.current_state,
                                                       'next_state': ProposalState.PUBLISHED}, postargs={'state': '1'})
        p.refresh_from_db()
        self.assertTrue(p.current_state == ProposalState.PUBLISHED)
        _, post_request = self.executeView(viewkwargs={'proposal_id': p.id, 'current_state': p.current_state,
                                                       'next_state': ProposalState.ON_HOLD}, postargs={'state': '1'})
        p.refresh_from_db()
        self.assertTrue(p.current_state == ProposalState.ON_HOLD)
        _, post_request = self.executeView(viewkwargs={'proposal_id': p.id, 'current_state': p.current_state,
                                                       'next_state': ProposalState.ARCHIVED}, postargs={'state': '1'})
        p.refresh_from_db()
        self.assertTrue(p.current_state == ProposalState.ARCHIVED)
