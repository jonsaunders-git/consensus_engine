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

from consensus_engine.models import Proposal, ChoiceTicket

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
        self.object.save()
        print(self.get_success_url())
        return HttpResponseRedirect(self.get_success_url())
