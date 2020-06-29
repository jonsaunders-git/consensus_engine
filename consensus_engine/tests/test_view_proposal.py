from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import OneUserMixin, ProposalGroupMixin, ViewMixin, ProposalMixin, TemplateViewMixin
from django.utils import timezone

from consensus_engine.views import ProposalView
from consensus_engine.models import ProposalGroup, Proposal, ProposalChoice, ChoiceTicket

class PickProposalGroupViewTest(OneUserMixin, TestCase,
                                 ProposalMixin, TemplateViewMixin):
    path = 'proposals/<int:proposal_id>'
    view = ProposalView

    def setUp(self):
        self.factory = RequestFactory()
        OneUserMixin.setUp(self)

    def test_view_new_proposal(self):
        p = self.create_new_proposal()
        context, _ = self.executeView(viewkwargs={'proposal_id' : p.id})
        self.assertTrue(context['proposal'] is not None)
        p2 = context['proposal']
        self.assertTrue(p2.id == p.id)
        self.assertTrue(context['current_choice'] is None)
        self.assertTrue(context['active_choices'].count() == 0)

    def test_view_new_proposal_with_choices(self):
        p = self.create_proposal_with_two_proposal_choices()
        context, _ = self.executeView(viewkwargs={'proposal_id' : p.id})
        self.assertTrue(context['proposal'] is not None)
        p2 = context['proposal']
        self.assertTrue(p2.id == p.id)
        self.assertTrue(context['current_choice'] is None)
        self.assertTrue(context['active_choices'].count() == 2)
        self.assertTrue(len(context['vote_spread']) == 2)

    def test_view_new_proposal_with_choices_and_votes(self):
        p = self.create_proposal_with_two_proposal_choices()
        # check that total votes = 0 if there are no votes
        pc1 = p.proposalchoice_set.first()
        pc2 = p.proposalchoice_set.last()
        v = ChoiceTicket.objects.create(user=self.user,
            date_chosen=timezone.now(), proposal_choice=pc1, current=True)
        context, _ = self.executeView(viewkwargs={'proposal_id' : p.id})
        self.assertTrue(context['proposal'] is not None)
        p2 = context['proposal']
        self.assertTrue(p2.id == p.id)
        self.assertTrue(context['current_choice'].id == v.id)
        self.assertTrue(context['active_choices'].count() == 2)
        self.assertTrue(len(context['vote_spread']) == 2)
        self.assertTrue(context['vote_spread'][1]['text'] == "Yes")
        self.assertTrue(context['vote_spread'][1]['count'] == 1)
        self.assertTrue(context['vote_spread'][1]['percentage'] == 100.0)
        self.assertTrue(context['vote_spread'][2]['text'] == "No")
        self.assertTrue(context['vote_spread'][2]['count'] == 0)
        self.assertTrue(context['vote_spread'][2]['percentage'] == 0)
