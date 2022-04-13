from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from urllib.parse import urlparse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404
from consensus_engine.models import ChoiceTicket, Proposal, ProposalChoice
DOMAINS_WHITELIST = ['localhost', 'quiet-bayou-98952.herokuapp.com']


@method_decorator(login_required, name='dispatch')
class MyVotesView(TemplateView):
    """ Shows a list of proposals """
    template_name = 'consensus_engine/view_my_votes.html'

    def get_context_data(self, **kwargs):
        votes_list = ChoiceTicket.objects.my_votes(self.request.user)
        context = {'votes_list': votes_list}
        return context


@method_decorator(login_required, name='dispatch')
class VoteView(TemplateView):
    """ Class based view for voting """
    template_name = 'consensus_engine/vote_proposal.html'

    def get_context_data(self, **kwargs):
        # view the proposal choices
        proposal = get_object_or_404(Proposal, pk=kwargs['proposal_id'])
        try:
            # should be just the one.
            current_choice = ChoiceTicket.objects.get(user=self.request.user,
                                                      proposal_choice__proposal=proposal,
                                                      state=proposal.state,
                                                      current=True)
        except (KeyError, ChoiceTicket.DoesNotExist):
            current_choice = None
        active_choices = proposal.proposalchoice_set.activated()
        context = {'proposal': proposal, 'current_choice': current_choice,
                   'active_choices': active_choices}
        return context

    def post(self, request, **kwargs):
        proposal = get_object_or_404(Proposal, pk=kwargs['proposal_id'])
        try:
            selected_choice = proposal.proposalchoice_set.get(pk=request.POST['choice'])
            selected_choice.vote(request.user)
        except (KeyError, ProposalChoice.DoesNotExist):
            return render(request, 'consensus_engine/vote_proposal.html', {
                'proposal': proposal,
                'error_message': "You didn't select a choice.",
            })
        url = request.POST.get('next', '/')
        parsed_uri = urlparse(url)
        if parsed_uri.netloc in DOMAINS_WHITELIST:
            return HttpResponseRedirect(url)  # Compliant
        return HttpResponseRedirect("/")
