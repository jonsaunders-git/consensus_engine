from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User

from .mixins import TwoUserMixin, ProposalMixin
# Create your tests here.

from consensus_engine.models import Proposal, ProposalChoice, ChoiceTicket, ProposalGroup
from consensus_engine.choice_templates import ChoiceTemplates
from consensus_engine.utils import ProposalState
from consensus_engine.exceptions import ProposalStateInvalid
from django.utils import timezone


# models test
class ProposalTest(TwoUserMixin, ProposalMixin, TestCase):

    def test_proposal_creation(self):
        w = self.create_new_proposal()
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(w.date_proposed <= timezone.now())
        self.assertTrue(w.proposal_name == "only a test")
        self.assertTrue(w.proposal_description == "yes, this is only a test")
        self.assertTrue(w.owned_by == self.user)
        self.assertTrue(w.state == ProposalState.DRAFT)

    def test_proposal_short_name(self):
        w = self.create_new_proposal()
        self.assertTrue(w.short_name == "only a test")
        x = self.create_new_proposal(
            proposal_name="this is a long test name and should be truncated"
        )
        self.assertTrue(x.short_name == "this is a long test name an...")
        x = self.create_new_proposal(proposal_name="this is a long test name anxyz")
        self.assertTrue(x.short_name == "this is a long test name anxyz")

    def test_total_votes_for_new_proposal(self):
        w = self.create_new_proposal()
        self.assertTrue(w.total_votes == 0)

    def test_proposal_creation_with_two_proposal_choices(self):
        w = self.create_proposal_with_two_proposal_choices()
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(w.proposalchoice_set.count() == 2)
        pc1 = w.proposalchoice_set.first()
        self.assertTrue(isinstance(pc1, ProposalChoice))
        pc2 = w.proposalchoice_set.last()
        self.assertTrue(isinstance(pc2, ProposalChoice))

    def test_total_votes_for_proposal_with_two_proposal_choices_with_voting(self):
        w = self.create_proposal_with_two_proposal_choices()
        # check that total votes = 0 if there are no votes
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(w.total_votes == 0)
        pc1 = w.proposalchoice_set.first()
        pc2 = w.proposalchoice_set.last()
        v = ChoiceTicket.objects.create(user=self.user,
            date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(w.total_votes == 1)
        # change votes - change current
        v2 = ChoiceTicket.objects.create(user=self.user,
            date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        v.current=False;
        v.save();
        self.assertTrue(w.total_votes == 1)
        # create a vote by another user and test that we have two votes
        v3 = ChoiceTicket.objects.create(user=self.user2,
            date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(w.total_votes == 2)

    def test_total_votes_for_proposal_with_a_deactivated_proposal_choice(self):
        w = self.create_proposal_with_two_proposal_choices()
        # check that total votes = 0 if there are no votes
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(w.total_votes == 0)
        pc1 = w.proposalchoice_set.first()
        pc2 = w.proposalchoice_set.last()
        v = ChoiceTicket.objects.create(user=self.user, date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(w.total_votes == 1)
        # change votes - change current
        v2 = ChoiceTicket.objects.create(user=self.user, date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        v.current=False;
        v.save();
        self.assertTrue(w.total_votes == 1)
        # create a vote by another user and test that we have two votes
        v3 = ChoiceTicket.objects.create(user=self.user2, date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        self.assertTrue(isinstance(v, ChoiceTicket))
        self.assertTrue(w.total_votes == 2)


    def test_proposal_owned_set(self):
        # should be no proposals for this user at start of test
        self.assertTrue(Proposal.objects.owned(self.user).count() == 0)
        # add one
        p = self.create_new_proposal()
        self.assertTrue(Proposal.objects.owned(self.user).count() == 1)
        # add another
        p1 = self.create_new_proposal()
        self.assertTrue(Proposal.objects.owned(self.user).count() == 2)
        # add one for the secind user
        p2 = self.create_new_proposal(owned_by=self.user2)
        # two for user 1 and 1 for user 2
        self.assertTrue(Proposal.objects.owned(self.user).count() == 2)
        self.assertTrue(Proposal.objects.owned(self.user2).count() == 1)

    def test_proposal_in_group_creation(self):
        g = ProposalGroup.objects.create(group_name="Test Group", owned_by=self.user, group_description="it's only a test group")
        w = self.create_new_proposal(proposal_group=g)
        self.assertTrue(isinstance(w, Proposal))
        self.assertTrue(w.date_proposed <= timezone.now())
        self.assertTrue(w.proposal_name == "only a test")
        self.assertTrue(w.proposal_description == "yes, this is only a test")
        self.assertTrue(w.owned_by == self.user)

    def test_proposal_in_group_set(self):
        g = ProposalGroup.objects.create(group_name="Test Group", owned_by=self.user, group_description="it's only a test group")
        # should be no proposals for this user at start of test
        self.assertTrue(Proposal.objects.in_group(g).count() == 0)
        # add one
        p = self.create_new_proposal(proposal_group=g)
        self.assertTrue(Proposal.objects.in_group(g).count() == 1)
        # add another
        p1 = self.create_new_proposal(proposal_group=g)
        self.assertTrue(Proposal.objects.in_group(g).count() == 2)
        g2 = ProposalGroup.objects.create(group_name="Test Group 2", owned_by=self.user, group_description="it's only a test group")
        # add one for the second group
        p2 = self.create_new_proposal(proposal_group=g2)
        # two for group 1 and 1 for group 2
        self.assertTrue(Proposal.objects.in_group(g).count() == 2)
        self.assertTrue(Proposal.objects.in_group(g2).count() == 1)

    def test_get_active_choices(self):
        p = self.create_proposal_with_two_proposal_choices()
        # no votes
        c = p.determine_consensus()
        self.assertTrue(c is None)
        self.assertTrue(ProposalChoice.objects.filter(proposal=p, current_consensus=True).count()==0)
        # add a vote
        pc1 = p.proposalchoice_set.first()
        pc2 = p.proposalchoice_set.last()
        v = ChoiceTicket.objects.create(user=self.user, date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        c2 = p.determine_consensus()
        self.assertTrue(c2.id == pc1.id and c2.current_consensus == True)
        self.assertTrue(ProposalChoice.objects.filter(proposal=p, current_consensus=True).count()==1)
        pc1.refresh_from_db()
        pc2.refresh_from_db()
        self.assertTrue(pc1.current_consensus==True)
        self.assertTrue(pc2.current_consensus==False)
        # add a vote to the other choice
        v2 = ChoiceTicket.objects.create(user=self.user2, date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        c3 = p.determine_consensus()
        self.assertTrue(c3 is None)
        self.assertTrue(ProposalChoice.objects.filter(proposal=p, current_consensus=True).count()==0)
        pc1.refresh_from_db()
        pc2.refresh_from_db()
        self.assertTrue(pc1.current_consensus==False)
        self.assertTrue(pc2.current_consensus==False)
        # remove the first vote
        v.current = False
        v.save()
        c4 = p.determine_consensus()
        self.assertTrue(c4.id == pc2.id and c4.current_consensus == True)
        self.assertTrue(ProposalChoice.objects.filter(proposal=p, current_consensus=True).count()==1)
        pc1.refresh_from_db()
        pc2.refresh_from_db()
        self.assertTrue(pc1.current_consensus==False)
        self.assertTrue(pc2.current_consensus==True)
        # add a vote for user 1 to the second choice
        v3 = ChoiceTicket.objects.create(user=self.user, date_chosen=timezone.now(), proposal_choice=pc2, current=True)
        c5 = p.determine_consensus()
        self.assertTrue(c5.id == pc2.id and c5.current_consensus == True)
        self.assertTrue(ProposalChoice.objects.filter(proposal=p, current_consensus=True).count()==1)
        pc1.refresh_from_db()
        pc2.refresh_from_db()
        self.assertTrue(pc1.current_consensus==False)
        self.assertTrue(pc2.current_consensus==True)
        # change the vote to pc1
        v3.current = False
        v3.save()
        v4 = ChoiceTicket.objects.create(user=self.user, date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        c6 = p.determine_consensus()
        self.assertTrue(c6 is None)
        self.assertTrue(ProposalChoice.objects.filter(proposal=p, current_consensus=True).count()==0)
        pc1.refresh_from_db()
        pc2.refresh_from_db()
        self.assertTrue(pc1.current_consensus==False)
        self.assertTrue(pc2.current_consensus==False)

    def test_populate_proposal_from_template(self):
        p = self.create_new_proposal()
        self.populate_from_template(p, ChoiceTemplates.genericMoscow)

    def test_populate_proposal_from_template_yes_no(self):
        p = self.create_new_proposal()
        self.populate_from_template(p, ChoiceTemplates.genericYesNo)

    def test_populate_proposal_from_template_1_to_5(self):
        p = self.create_new_proposal()
        self.populate_from_template(p, ChoiceTemplates.generic1to5)

    def test_populate_proposal_from_template_none(self):
        p = self.create_new_proposal()
        self.populate_from_template(p, None)

    def test_populate_exising_proposal_from_template(self):
        p = self.create_proposal_with_two_proposal_choices()
        self.populate_from_template(p, ChoiceTemplates.genericMoscow)

    def test_get_current_vote_spread(self):
        # create a proposal and populate it from the MoSCow template
        p = self.create_new_proposal()
        self.populate_from_template(p, ChoiceTemplates.genericMoscow)
        # get voting spread for current time, returns a dictionary with all the
        # choices and their current votes
        s = p.get_voting_spread()
        # check it is 0 for all choices
        self.assertTrue(len(s) == 4)
        cs = ["", "Must have", "Should have", "Could have", "Wishlist"]
        for c in range(1,4):
            self.assertTrue(s[c]['text'] == cs[c])
            self.assertTrue(s[c]['count'] == 0)
            self.assertTrue(s[c]['percentage'] == 0)
        # vote on a choice
        ac = p.get_active_choices()
        pc = ac.first()
        pc.vote(self.user)
        s2 = p.get_voting_spread()
        for c2 in range(1,4):
            if c2 == pc.id:
                self.assertTrue(s2[c2]['text'] == cs[c2])
                self.assertTrue(s2[c2]['count'] == 1)
                self.assertTrue(s2[c2]['percentage'] == 100.0)
            else:
                self.assertTrue(s2[c2]['text'] == cs[c2])
                self.assertTrue(s2[c2]['count'] == 0)
                self.assertTrue(s2[c2]['percentage'] == 0)

    def test_proposal_state(self):
        # change the state and check the value
        p = self.create_new_proposal()
        self.assertTrue(p.state == ProposalState.DRAFT)
        p.trial()
        self.assertTrue(p.state == ProposalState.TRIAL)
        p.publish()
        self.assertTrue(p.state == ProposalState.PUBLISHED)
        p.hold()
        self.assertTrue(p.state == ProposalState.ON_HOLD)
        p.archive()
        self.assertTrue(p.state == ProposalState.ARCHIVED)

    def test_proposal_draft(self):
        # change the state and check the value
        p = self.create_new_proposal()
        self.assertTrue(p.state == ProposalState.DRAFT)
        # trial is okay
        p.trial()
        self.assertTrue(p.state == ProposalState.TRIAL)
        # check we can't redo trial
        with self.assertRaises(ProposalStateInvalid) as e:
            p.trial()
        # change the state and check the value
        p2 = self.create_new_proposal()
        p2.publish()
        self.assertTrue(p2.state == ProposalState.PUBLISHED)
        with self.assertRaises(ProposalStateInvalid) as e2:
            p2.publish()
        # change the state and check the value
        p3 = self.create_new_proposal()
        p3.hold()
        self.assertTrue(p3.state == ProposalState.ON_HOLD)
        with self.assertRaises(ProposalStateInvalid) as e3:
            p3.hold()
        # change the state and check the value
        p4 = self.create_new_proposal()
        p4.archive()
        self.assertTrue(p4.state == ProposalState.ARCHIVED)
        with self.assertRaises(ProposalStateInvalid) as e4:
            p4.archive()

    def test_proposal_trial(self):
        # change the state and check the value
        p = self.create_new_proposal()
        # trial is okay
        p.trial()
        self.assertTrue(p.state == ProposalState.TRIAL)
        # change the state and check the value
        p2 = self.create_new_proposal()
        p2.trial()
        p2.publish()
        self.assertTrue(p2.state == ProposalState.PUBLISHED)
        with self.assertRaises(ProposalStateInvalid) as e2:
            p2.publish()
        # change the state and check the value
        p3 = self.create_new_proposal()
        p3.trial()
        p3.hold()
        self.assertTrue(p3.state == ProposalState.ON_HOLD)
        with self.assertRaises(ProposalStateInvalid) as e3:
            p3.hold()
        # change the state and check the value
        p4 = self.create_new_proposal()
        p4.trial()
        p4.archive()
        self.assertTrue(p4.state == ProposalState.ARCHIVED)
        with self.assertRaises(ProposalStateInvalid) as e4:
            p4.archive()

    def test_proposal_publish(self):
        # change the state and check the value
        p = self.create_new_proposal()
        p.publish()
        self.assertTrue(p.state == ProposalState.PUBLISHED)
        # change the state and check the value
        p2 = self.create_new_proposal()
        p2.publish()
        with self.assertRaises(ProposalStateInvalid) as e2:
            p2.trial()
        # change the state and check the value
        p3 = self.create_new_proposal()
        p3.publish()
        p3.hold()
        self.assertTrue(p3.state == ProposalState.ON_HOLD)
        with self.assertRaises(ProposalStateInvalid) as e3:
            p3.hold()
        # change the state and check the value
        p4 = self.create_new_proposal()
        p4.trial()
        p4.archive()
        self.assertTrue(p4.state == ProposalState.ARCHIVED)
        with self.assertRaises(ProposalStateInvalid) as e4:
            p4.archive()

    def test_proposal_hold(self):
        # change the state and check the value
        p = self.create_new_proposal()
        p.hold()
        self.assertTrue(p.state == ProposalState.ON_HOLD)
        # change the state and check the value
        p2 = self.create_new_proposal()
        p2.hold()
        with self.assertRaises(ProposalStateInvalid) as e2:
            p2.trial()
        # change the state and check the value
        p3 = self.create_new_proposal()
        p3.hold()
        p3.publish()
        self.assertTrue(p3.state == ProposalState.PUBLISHED)
        with self.assertRaises(ProposalStateInvalid) as e3:
            p3.publish()
        # change the state and check the value
        p4 = self.create_new_proposal()
        p4.trial()
        p4.archive()
        self.assertTrue(p4.state == ProposalState.ARCHIVED)
        with self.assertRaises(ProposalStateInvalid) as e4:
            p4.archive()

    def test_proposal_archive(self):
        # change the state and check the value
        p = self.create_new_proposal()
        p.archive()
        self.assertTrue(p.state == ProposalState.ARCHIVED)
        # change the state and check the value
        p2 = self.create_new_proposal()
        p2.archive()
        with self.assertRaises(ProposalStateInvalid) as e2:
            p2.trial()
        # change the state and check the value
        p3 = self.create_new_proposal()
        p3.archive()
        with self.assertRaises(ProposalStateInvalid) as e3:
            p3.publish()
        # change the state and check the value
        p4 = self.create_new_proposal()
        p4.archive()
        with self.assertRaises(ProposalStateInvalid) as e4:
            p4.hold()
