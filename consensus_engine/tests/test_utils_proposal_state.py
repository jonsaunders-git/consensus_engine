from django.test import TestCase
from consensus_engine.utils import ProposalState

class ProposalStateTest(TestCase):

    def test_draft(self):
        s = ProposalState.DRAFT
        l = s.get_next_states()
        self.assertTrue(len(l) == 4)
        self.assertTrue(l[0] == ProposalState.TRIAL)
        self.assertTrue(l[1] == ProposalState.PUBLISHED)
        self.assertTrue(l[2] == ProposalState.ON_HOLD)
        self.assertTrue(l[3] == ProposalState.ARCHIVED)

    def test_trial(self):
        s = ProposalState.TRIAL
        l = s.get_next_states()
        self.assertTrue(len(l) == 3)
        self.assertTrue(l[0] == ProposalState.PUBLISHED)
        self.assertTrue(l[1] == ProposalState.ON_HOLD)
        self.assertTrue(l[2] == ProposalState.ARCHIVED)

    def test_published(self):
        s = ProposalState.PUBLISHED
        l = s.get_next_states()
        self.assertTrue(len(l) == 2)
        self.assertTrue(l[0] == ProposalState.ON_HOLD)
        self.assertTrue(l[1] == ProposalState.ARCHIVED)

    def test_on_hold(self):
        s = ProposalState.ON_HOLD
        l = s.get_next_states()
        self.assertTrue(len(l) == 2)
        self.assertTrue(l[0] == ProposalState.PUBLISHED)
        self.assertTrue(l[1] == ProposalState.ARCHIVED)

    def test_on_hold(self):
        s = ProposalState.ARCHIVED
        l = s.get_next_states()
        self.assertTrue(len(l) == 0)
