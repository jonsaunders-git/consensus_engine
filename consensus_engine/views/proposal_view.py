from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from consensus_engine.models import Proposal, ChoiceTicket, ProposalGroup

@method_decorator(login_required, name='dispatch')
class ProposalView(TemplateView):
    template_name = 'consensus_engine/view_proposal.html'

    def get_context_data(self, **kwargs):
        # view the proposal choices
        proposal = get_object_or_404(Proposal, pk=self.kwargs['proposal_id'])
        current_choice = ChoiceTicket.objects.get_current_choice(
                                user=self.request.user,
                                proposal=proposal)
        active_choices = proposal.proposalchoice_set.activated()
        context = { 'proposal' : proposal, 'current_choice' : current_choice,
                    'active_choices' : active_choices }
        return context


@method_decorator(login_required, name='dispatch')
class CreateProposalView(CreateView):
    template_name = 'consensus_engine/new_proposal.html'
    model = Proposal
    fields = ['proposal_name', 'proposal_description']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.date_proposed = timezone.now()
        if 'proposal_group_id' in self.kwargs:
            proposal_group = ProposalGroup.objects.get(pk=self.kwargs['proposal_group_id'])
            self.object.proposal_group = proposal_group
        self.object.save()
        print(self.get_success_url())
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        # add the proposal_group to the context of it exists
        context = super().get_context_data(**kwargs)
        if 'proposal_group_id' in self.kwargs:
            proposal_group = ProposalGroup.objects.get(pk=self.kwargs['proposal_group_id'])
            context['proposal_group'] = proposal_group
        return context
