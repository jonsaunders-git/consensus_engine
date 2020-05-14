from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User

from .mixins import TwoUserMixin, ProposalMixin

# Create your tests here.

from consensus_engine.models import (Proposal, ProposalChoice, ChoiceTicket,
                                        ProposalGroup)
from django.utils import timezone


# models test
class ChoiceTicketTest(TwoUserMixin, ProposalMixin, TestCase):

    def test_choiceticket_creation(self):
        w = self.create_proposal_with_two_proposal_choices()
        self.assertTrue(w.proposalchoice_set.count() == 2)
        dt = timezone.now()
        pc1 = w.proposalchoice_set.first()
        v = ChoiceTicket.objects.create(user=self.user,
            date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(v.date_chosen <= timezone.now() and v.date_chosen >= dt)
        self.assertTrue(v.user == self.user)
        self.assertTrue(v.proposal_choice == pc1)
        self.assertTrue(v.current == True)

    def test_my_votes_with_with_voting(self):
        w = self.create_proposal_with_two_proposal_choices()
        # check that total votes = 0 if there are no votes
        self.assertTrue(isinstance(w, Proposal))
        pc1 = w.proposalchoice_set.first()
        pc2 = w.proposalchoice_set.last()
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 0)
        v = ChoiceTicket.objects.create(user=self.user,
            date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        # test my_votes
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 1)
        # change votes - change current
        v2 = ChoiceTicket.objects.create(user=self.user,
            date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        v.current=False;
        v.save();
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 1)
        # create a vote by another user and test that we have two votes
        v3 = ChoiceTicket.objects.create(user=self.user2,
            date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        # test my_votes
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 1)

    def test_my_votes_with_voting_with_a_deactivated_proposal_choice(self):
        w = self.create_proposal_with_two_proposal_choices()
        # check that total votes = 0 if there are no votes
        self.assertTrue(isinstance(w, Proposal))
        pc1 = w.proposalchoice_set.first()
        pc2 = w.proposalchoice_set.last()
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 0)
        v = ChoiceTicket.objects.create(user=self.user,
            date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 1)
        # change votes - change current
        v2 = ChoiceTicket.objects.create(user=self.user,
            date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        v.current=False;
        v.save();
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 1)
        # create a vote by another user and test that we have two votes
        v3 = ChoiceTicket.objects.create(user=self.user2,
            date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        # test my_votes
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 1)
        # deactivate the other proposal_choice
        pc1.deactivated_date = timezone.now()
        pc1.save()
        x = ChoiceTicket.objects.my_votes(self.user)
        self.assertTrue(x.count() == 1)
        # deactivate the proposal_choice
        pc2.deactivated_date = timezone.now()
        pc2.save()
        x2 = ChoiceTicket.objects.my_votes(self.user)
        self.assertTrue(x2.count() == 0)

    def test_my_votes_with_multiple_votes(self):
        w = self.create_proposal_with_two_proposal_choices()
        self.assertTrue(isinstance(w, Proposal))
        pc1 = w.proposalchoice_set.first()
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 0)
        v = ChoiceTicket.objects.create(user=self.user,
            date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 1)
        v3 = ChoiceTicket.objects.create(user=self.user2,
            date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user2).count() == 1)
        # test my_votes
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 1)
        # create another proposal to vote on
        w2 = self.create_proposal_with_two_proposal_choices()
        self.assertTrue(isinstance(w, Proposal))
        pc2 = w2.proposalchoice_set.first()
        pc3 = w2.proposalchoice_set.last()
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 1)
        v = ChoiceTicket.objects.create(user=self.user,
            date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 2)
        # create another vote for another user
        v3 = ChoiceTicket.objects.create(user=self.user2,
            date_chosen=timezone.now(), proposal_choice=pc3, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        # test my_votes
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user).count() == 2)
        # deactivate the proposal_choice
        pc2.deactivated_date = timezone.now()
        pc2.save()
        x2 = ChoiceTicket.objects.my_votes(self.user)
        self.assertTrue(x2.count() == 1)
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user2).count() == 2)
        # deactivate the proposal_choice
        pc3.deactivated_date = timezone.now()
        pc3.save()
        self.assertTrue(ChoiceTicket.objects.my_votes(self.user2).count() == 1)
