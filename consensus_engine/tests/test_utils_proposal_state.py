from django.test import TestCase
from consensus_engine.utils import ProposalState


class ProposalStateTest(TestCase):

    def test_draft(self):
        s = ProposalState.DRAFT
        sl = s.get_next_states()
        self.assertTrue(len(sl) == 4)
        self.assertTrue(sl[0] == ProposalState.TRIAL)
        self.assertTrue(sl[1] == ProposalState.PUBLISHED)
        self.assertTrue(sl[2] == ProposalState.ON_HOLD)
        self.assertTrue(sl[3] == ProposalState.ARCHIVED)

    def test_trial(self):
        s = ProposalState.TRIAL
        sl = s.get_next_states()
        self.assertTrue(len(sl) == 3)
        self.assertTrue(sl[0] == ProposalState.PUBLISHED)
        self.assertTrue(sl[1] == ProposalState.ON_HOLD)
        self.assertTrue(sl[2] == ProposalState.ARCHIVED)

    def test_published(self):
        s = ProposalState.PUBLISHED
        sl = s.get_next_states()
        self.assertTrue(len(sl) == 2)
        self.assertTrue(sl[0] == ProposalState.ON_HOLD)
        self.assertTrue(sl[1] == ProposalState.ARCHIVED)

    def test_on_hold(self):
        s = ProposalState.ON_HOLD
        sl = s.get_next_states()
        self.assertTrue(len(sl) == 2)
        self.assertTrue(sl[0] == ProposalState.PUBLISHED)
        self.assertTrue(sl[1] == ProposalState.ARCHIVED)

    def test_archived(self):
        s = ProposalState.ARCHIVED
        sl = s.get_next_states()
        self.assertTrue(len(sl) == 0)
