from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User

from .mixins import TwoUserMixin, ProposalMixin

# Create your tests here.

from consensus_engine.models import Proposal, ProposalChoice, ChoiceTicket
from consensus_engine.models import ConsensusHistory
from consensus_engine.choice_templates import ChoiceTemplates
from django.utils import timezone


# models test
class ConsensusHistoryTest(TwoUserMixin, ProposalMixin, TestCase):

    def test_snapshot(self):
        p = self.create_proposal_with_two_proposal_choices()
        dt = timezone.now()
        ss = ConsensusHistory.build_snapshot(p)
        ss.save()
        self.assertTrue(ss is not None)
        self.assertTrue(ss.snapshot_date >= dt and ss.snapshot_date <= timezone.now())
        self.assertTrue(ss.proposal.id == p.id)
        self.assertTrue(ss.consensus is None)
        no_votes_data = [
                         {'choice_id': 1, 'text': "Yes", 'count': 0},
                         {'choice_id': 2, 'text': "No", 'count': 0}
                        ]
        self.assertTrue(ss.get_consensus_data() == no_votes_data)
        pc = p.proposalchoice_set.first()
        pc.vote(self.user)
        ss2 = ConsensusHistory.objects.at_date(proposal=p, at_date=timezone.now())
        one_vote_data = [
                         {'choice_id': 1, 'text': "Yes", 'count': 1},
                         {'choice_id': 2, 'text': "No", 'count': 0}
                        ]
        self.assertTrue(ss2.get_consensus_data() == one_vote_data)
        all_history = ConsensusHistory.objects.all_history_for_proposal(p)
        self.assertTrue(all_history.count() == 2)
