from django.test import TestCase, RequestFactory
from .mixins import TwoUserMixin, ProposalGroupMixin, ProposalMixin, TemplateViewMixin
from django.utils import timezone
from consensus_engine.views import MyVotesView, VoteView
from consensus_engine.models import ChoiceTicket


class MyVotesViewTest(TwoUserMixin, TestCase,
                      ProposalGroupMixin, ProposalMixin, TemplateViewMixin):
    view = MyVotesView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_list_votes_no_votes(self):
        context, _ = self.executeView()
        self.assertTrue(context['votes_list'].count() == 0)

    def test_list_votes_some_votes(self):
        p = self.create_proposal_with_two_proposal_choices()
        p.publish()
        # check that total votes = 0 if there are no votes
        pc1 = p.proposalchoice_set.first()
        _ = ChoiceTicket.objects.create(user=self.user,
                                        date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        context, _ = self.executeView()
        self.assertTrue(context['votes_list'].count() == 1)
        p2 = self.create_proposal_with_two_proposal_choices()
        p2.publish()
        pc3 = p2.proposalchoice_set.first()
        _ = ChoiceTicket.objects.create(user=self.user,
                                        date_chosen=timezone.now(), proposal_choice=pc3, current=True)
        context, _ = self.executeView()
        self.assertTrue(context['votes_list'].count() == 2)
        _ = ChoiceTicket.objects.create(user=self.user2,
                                        date_chosen=timezone.now(), proposal_choice=pc3, current=True)
        context, _ = self.executeView()
        self.assertTrue(context['votes_list'].count() == 2)
        # switch user
        self.current_user = self.user2
        context, _ = self.executeView()
        self.assertTrue(context['votes_list'].count() == 1)


class VoteViewTest(TwoUserMixin, TestCase,
                   ProposalGroupMixin, ProposalMixin, TemplateViewMixin):
    view = VoteView

    def setUp(self):
        self.factory = RequestFactory()
        TwoUserMixin.setUp(self)

    def test_vote(self):
        p = self.create_proposal_with_two_proposal_choices()
        p.publish()
        # check that total votes = 0 if there are no votes
        pc1 = p.proposalchoice_set.first()
        pc2 = p.proposalchoice_set.last()
        self.assertTrue(p.total_votes == 0)
        self.assertTrue(ChoiceTicket.objects.filter(proposal_choice=pc1).count() == 0)
        self.assertTrue(ChoiceTicket.objects.filter(proposal_choice=pc2).count() == 0)
        context, _ = self.executeView(viewkwargs={'proposal_id': p.id}, postargs={'choice': pc1.id})
        self.assertTrue(p.total_votes == 1)
        self.assertTrue(ChoiceTicket.objects.filter(proposal_choice=pc1).count() == 1)
        self.assertTrue(ChoiceTicket.objects.filter(proposal_choice=pc2).count() == 0)

    def test_vote_incorrect_choice(self):
        p = self.create_proposal_with_two_proposal_choices()
        p.publish()
        # check that total votes = 0 if there are no votes
        pc1 = p.proposalchoice_set.first()
        pc2 = p.proposalchoice_set.last()
        self.assertTrue(p.total_votes == 0)
        self.assertTrue(ChoiceTicket.objects.filter(proposal_choice=pc1).count() == 0)
        self.assertTrue(ChoiceTicket.objects.filter(proposal_choice=pc2).count() == 0)
        context, _ = self.executeView(viewkwargs={'proposal_id': p.id}, postargs={'choice': 99})
        self.assertTrue(p.total_votes == 0)
        self.assertTrue(ChoiceTicket.objects.filter(proposal_choice=pc1).count() == 0)
        self.assertTrue(ChoiceTicket.objects.filter(proposal_choice=pc2).count() == 0)
