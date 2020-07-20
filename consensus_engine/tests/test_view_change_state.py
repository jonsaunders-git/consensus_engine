from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import OneUserMixin, ViewMixin, ProposalMixin, TemplateViewMixin
from django.utils import timezone

from consensus_engine.views import StateView
from consensus_engine.models import Proposal
from consensus_engine.utils import ProposalState
from consensus_engine.exceptions import ProposalStateInvalid

class StateViewTest(OneUserMixin, TestCase,
                    ProposalMixin, TemplateViewMixin):
    view = StateView

    def setUp(self):
        self.factory = RequestFactory()
        OneUserMixin.setUp(self)

    def test_change_state(self):
        p = self.create_new_proposal()
        self.assertTrue(p.current_state == ProposalState.DRAFT)
        context , _ = self.executeView(viewkwargs={'proposal_id' : p.id}, postargs={'state' : '1'})
        p.refresh_from_db()
        self.assertTrue(p.current_state == ProposalState.TRIAL)
        context , _ = self.executeView(viewkwargs={'proposal_id' : p.id}, postargs={'state' : '2'})
        p.refresh_from_db()
        self.assertTrue(p.current_state == ProposalState.PUBLISHED)
        context , _ = self.executeView(viewkwargs={'proposal_id' : p.id}, postargs={'state' : '3'})
        p.refresh_from_db()
        self.assertTrue(p.current_state == ProposalState.ON_HOLD)
        context , _ = self.executeView(viewkwargs={'proposal_id' : p.id}, postargs={'state' : '4'})
        p.refresh_from_db()
        self.assertTrue(p.current_state == ProposalState.ARCHIVED)

    def test_change_incorrect_state(self):
        p = self.create_new_proposal()
        self.assertTrue(p.current_state == ProposalState.DRAFT)
        context , _ = self.executeView(viewkwargs={'proposal_id' : p.id}, postargs={'state' : '1'})
        p.refresh_from_db()
        self.assertTrue(p.current_state == ProposalState.TRIAL)
        with self.assertRaises(ProposalStateInvalid) as e:
            context , _ = self.executeView(viewkwargs={'proposal_id' : p.id}, postargs={'state' : '0'})

    def test_key_error(self):
        p = self.create_new_proposal()
        self.assertTrue(p.current_state == ProposalState.DRAFT)
        _ , response = self.executeView(viewkwargs={'proposal_id' : p.id}, postargs={})
        content = str(response.content)
        self.assertTrue(content.find("You didn&#x27;t select a state.") > 0)
