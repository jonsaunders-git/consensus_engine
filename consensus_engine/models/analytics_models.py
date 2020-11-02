from django.db import models
from django.utils import timezone
import json


class ConsensusHistoryManager(models.Manager):
    """ A manager to get the information for ConsensusHistory """

    def at_date(self, proposal, at_date):
        # make it the end of the day
        query_datetime = at_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        snapshot = ConsensusHistory.objects.filter(proposal=proposal,
                                                   snapshot_date__lte=query_datetime
                                                   ).latest('snapshot_date')
        return snapshot

    def all_history_for_proposal(self, proposal):
        history = ConsensusHistory.objects.all().order_by('snapshot_date')
        return history

    def earliest_snapshot(self, proposal):
        snapshot = ConsensusHistory.objects.filter(proposal=proposal
                                                   ).earliest('snapshot_date')
        return snapshot


class ConsensusHistory(models.Model):
    """
    Saves a snapshot of the vote at a particular time
    - snapshot data is stored in a list of dictionaries
    """
    snapshot_date = models.DateTimeField('snapshot date')
    proposal = models.ForeignKey('Proposal', on_delete=models.CASCADE)
    consensus = models.ForeignKey('ProposalChoice', on_delete=models.CASCADE, null=True)
    consensus_data = models.TextField()
    # manager
    objects = ConsensusHistoryManager()

    # class functions
    @classmethod
    def build_snapshot(cls, proposal):
        history_item = ConsensusHistory()
        history_item.snapshot(proposal)
        return history_item

    def snapshot(self, proposal):
        self.snapshot_date = timezone.now()
        self.proposal = proposal
        self.consensus = proposal.current_consensus
        data_list = []
        active_choices = proposal.get_active_choices()
        for choice in active_choices:
            data_element = {"choice_id": choice.id,
                            "text": choice.text,
                            "count": choice.current_vote_count}
            data_list.append(data_element)
        self.consensus_data = json.dumps(data_list)

    def get_consensus_data(self):
        return json.loads(self.consensus_data)
