from django.test import TestCase
from .mixins import TwoUserMixin, ProposalGroupMixin, ProposalMixin
from consensus_engine.models import Proposal, ChoiceTicket
from django.utils import timezone
from consensus_engine.templatetags.proposaltags import (visible_groups, total_votes, my_vote, current_consensus,
                                                        release_notes, user_search, proposal_state,
                                                        proposal_list_element)


class ProposalGroupTagsTest(TwoUserMixin, ProposalGroupMixin, TestCase):

    def test_proposal_tags_visible_groups(self):
        self.assertTrue(visible_groups(self.user)['visible_groups'].count() == 0)
        _ = self.create_proposal_group()
        self.assertTrue(visible_groups(self.user)['visible_groups'].count() == 1)
        _ = self.create_proposal_group()
        self.assertTrue(visible_groups(self.user)['visible_groups'].count() == 2)
        # add a group under another user and test to see if it works
        _ = self.create_proposal_group(owned_by=self.user2)
        self.assertTrue(visible_groups(self.user)['visible_groups'].count() == 2)
        self.assertTrue(visible_groups(self.user2)['visible_groups'].count() == 1)


class ProposalTagsTest(TwoUserMixin, ProposalMixin, TestCase):

    def test_proposal_tags_total_votes(self):
        w = self.create_proposal_with_two_proposal_choices()
        w.publish()
        # check that total votes = 0 if there are no votes
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(total_votes(w.id)['total_votes'] == 0)
        pc1 = w.proposalchoice_set.first()
        pc2 = w.proposalchoice_set.last()
        v = ChoiceTicket.objects.create(user=self.user,
                                        date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(total_votes(w.id)['total_votes'] == 1)
        # change votes - change current
        _ = ChoiceTicket.objects.create(user=self.user,
                                        date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        v.current = False
        v.save()
        self.assertTrue(total_votes(w.id)['total_votes'] == 1)
        # create a vote by another user and test that we have two votes
        _ = ChoiceTicket.objects.create(user=self.user2,
                                        date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(total_votes(w.id)['total_votes'] == 2)

    def test_proposal_tags_my_vote(self):
        w = self.create_proposal_with_two_proposal_choices()
        w.publish()
        self.assertTrue(my_vote(w.id, self.user.id)['my_vote'] == 'None')
        # vote for the first choice
        pc1 = w.proposalchoice_set.first()
        pc2 = w.proposalchoice_set.last()
        v = ChoiceTicket.objects.create(user=self.user,
                                        date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(my_vote(w.id, self.user.id)['my_vote'] == pc1.text)
        # change votes - change current
        _ = ChoiceTicket.objects.create(user=self.user,
                                        date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        v.current = False
        v.save()
        self.assertTrue(my_vote(w.id, self.user.id)['my_vote'] == pc2.text)
        # create a vote by another user and test that we have two votes
        _ = ChoiceTicket.objects.create(user=self.user2,
                                        date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(my_vote(w.id, self.user.id)['my_vote'] == pc2.text)
        self.assertTrue(my_vote(w.id, self.user2.id)['my_vote'] == pc1.text)
        self.assertTrue(pc1.text != pc2.text)

    def test_proposal_tags_current_consenus(self):
        w = self.create_proposal_with_two_proposal_choices()
        w.publish()
        # check that total votes = 0 if there are no votes
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(current_consensus(w.id)['current_consensus'] == 'No consensus')
        pc1 = w.proposalchoice_set.first()
        pc2 = w.proposalchoice_set.last()
        v = ChoiceTicket.objects.create(user=self.user,
                                        date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        w.determine_consensus()
        self.assertTrue(current_consensus(w.id)['current_consensus'] == 'Yes')
        # change votes - change current
        _ = ChoiceTicket.objects.create(user=self.user,
                                        date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        v.current = False
        v.save()
        w.determine_consensus()
        self.assertTrue(current_consensus(w.id)['current_consensus'] == 'No')
        # create a vote by another user and test that we have two votes
        _ = ChoiceTicket.objects.create(user=self.user2,
                                        date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        w.determine_consensus()
        self.assertTrue(current_consensus(w.id)['current_consensus'] == 'No consensus')

    def test_release_note(self):
        # to implement when I implement release notes
        release_notes()

    def test_user_search(self):
        # to implement when I implement user search
        user_search()

    def test_proposal_state(self):
        w = self.create_new_proposal()
        # check that total votes = 0 if there are no votes
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(total_votes(w.id)['total_votes'] == 0)
        l1 = proposal_state(w)
        self.assertTrue('proposal_state' in l1)
        self.assertTrue(l1['proposal_state'] == 'DRAFT')
        w.trial()
        l2 = proposal_state(w)
        self.assertTrue('proposal_state' in l2)
        self.assertTrue(l2['proposal_state'] == 'TRIAL')
        w.publish()
        l3 = proposal_state(w)
        self.assertTrue('proposal_state' in l3)
        self.assertTrue(l3['proposal_state'] == 'PUBLISHED')
        w.hold()
        l4 = proposal_state(w)
        self.assertTrue('proposal_state' in l4)
        self.assertTrue(l4['proposal_state'] == 'ON_HOLD')
        w.archive()
        l5 = proposal_state(w)
        self.assertTrue('proposal_state' in l5)
        self.assertTrue(l5['proposal_state'] == 'ARCHIVED')

    def test_proposal_list_element(self):
        p = self.create_new_proposal()
        proposal_list_element(p, 0)
