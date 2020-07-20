from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from consensus_engine.models import Proposal, ProposalState


@method_decorator(login_required, name='dispatch')
class StateView(TemplateView):
    """ Class based view for changing state """
    template_name = 'consensus_engine/change_state.html'

    def get_context_data(self, **kwargs):
        # view the proposal choices
        proposal = get_object_or_404(Proposal, pk=kwargs['proposal_id'])
        current_state = proposal.current_state

        possible_states = current_state.get_next_states()
        context = {'proposal': proposal, 'current_state': current_state,
                   'possible_states': possible_states}
        return context

    def post(self, request, **kwargs):
        proposal = get_object_or_404(Proposal, pk=kwargs['proposal_id'])
        try:
            selected_state = int(request.POST['state'])
            new_state = ProposalState(selected_state)
            if new_state == ProposalState.DRAFT:
                proposal.trial()
            if new_state == ProposalState.TRIAL:
                proposal.trial()
            elif new_state == ProposalState.PUBLISHED:
                proposal.publish()
            elif new_state == ProposalState.ON_HOLD:
                proposal.hold()
            elif new_state == ProposalState.ARCHIVED:
                proposal.archive()
        except (KeyError):
            return render(request, 'consensus_engine/change_state.html', {
                'proposal': proposal,
                'error_message': "You didn't select a state.",
            })
        success_url = reverse('view_proposal', args=[proposal.id])
        return HttpResponseRedirect(success_url)
