from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from consensus_engine.models import Proposal, ChoiceTicket, ProposalGroup
from consensus_engine.choice_templates import ChoiceTemplates


@method_decorator(login_required, name='dispatch')
class ProposalView(TemplateView):
    template_name = 'consensus_engine/view_proposal.html'

    def get_context_data(self, **kwargs):
        # view the proposal choices
        proposal = get_object_or_404(Proposal, pk=self.kwargs['proposal_id'])
        current_choice = ChoiceTicket.objects.get_current_choice(user=self.request.user,
                                                                 proposal=proposal)
        active_choices = proposal.proposalchoice_set.activated()
        vote_spread = proposal.get_voting_spread()
        context = {'proposal': proposal, 'current_choice': current_choice,
                   'active_choices': active_choices, 'vote_spread': vote_spread}
        return context


@method_decorator(login_required, name='dispatch')
class CreateProposalView(CreateView):
    template_name = 'consensus_engine/new_proposal.html'
    model = Proposal
    fields = ['proposal_name', 'proposal_description']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owned_by = self.request.user
        self.object.date_proposed = timezone.now()
        if 'proposal_group_id' in self.kwargs:
            proposal_group = ProposalGroup.objects.get(pk=self.kwargs['proposal_group_id'])
            self.object.proposal_group = proposal_group
        self.object.save()
        populate_option = int(self.request.POST["options"])
        population_types = [None,
                            ChoiceTemplates.genericMoscow,
                            ChoiceTemplates.genericYesNo,
                            ChoiceTemplates.generic1to5]
        self.object.populate_from_template(population_types[populate_option])
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        # add the proposal_group to the context of it exists
        context = super().get_context_data(**kwargs)
        if 'proposal_group_id' in self.kwargs:
            proposal_group = ProposalGroup.objects.get(pk=self.kwargs['proposal_group_id'])
            context['proposal_group'] = proposal_group
        return context


@method_decorator(login_required, name='dispatch')
class EditProposalView(UpdateView):
    template_name = 'consensus_engine/edit_proposal.html'
    model = Proposal
    fields = ['proposal_name', 'proposal_description']

    def form_valid(self, form):
        if self.object.user_can_edit(self.request.user):
            return super().form_valid(form)
        else:
            raise PermissionDenied("Editing is not allowed")


@method_decorator(login_required, name='dispatch')
class ProposalListView(TemplateView):
    """ Shows a list of proposals """
    template_name = 'consensus_engine/list_proposals.html'

    def get_context_data(self, **kwargs):
        # view the proposal choices
        proposals_list = Proposal.objects.owned(self.request.user)
        context = {'proposals_list': proposals_list}
        return context


@method_decorator(login_required, name='dispatch')
class ProposalListGroupView(ProposalListView):
    """ Sub class ProposalListView to get ones in group """

    def get_context_data(self, **kwargs):
        # view the proposal choices
        proposal_group = get_object_or_404(ProposalGroup, pk=kwargs['proposal_group_id'])
        proposals_list = Proposal.objects.in_group(proposal_group)
        context = {'proposals_list': proposals_list, 'proposal_group': proposal_group}
        return context
