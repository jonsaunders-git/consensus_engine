from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse

from .models import Proposal, ProposalChoice, ChoiceTicket, CurrentChoiceTicket

# Create your views here.

def index(request):
    return render(request, 'consensus_engine/index.html')

@login_required
def view_proposal(request, proposal_id):
    # view the proposal choices
    proposal = get_object_or_404(Proposal, pk=proposal_id)
    try:
        current_choice = CurrentChoiceTicket.objects.get(user = request.user, proposal = proposal)
    except (KeyError, CurrentChoiceTicket.DoesNotExist):
        current_choice = none

    context = {'proposal' : proposal, 'current_choice' : current_choice}
    return render(request, 'consensus_engine/list_proposal_choices.html', context)

@login_required
def new_proposal(request):
    return HttpResponse("You're looking at the enter proposal page.")

@login_required
def list_proposals(request):
    proposals_list = Proposal.objects.order_by('-date_proposed')[:5]
    context = {'proposals_list': proposals_list}
    return render(request, 'consensus_engine/list_proposals.html', context)

@login_required
def register_vote(request, proposal_id):
    proposal = get_object_or_404(Proposal, pk=proposal_id)
    try:
        selected_choice = proposal.proposalchoice_set.get(pk=request.POST['choice'])
    except (KeyError, ProposalChoice.DoesNotExist):
        return render(request, 'consensus_engine/list_proposal_choices.html', {
            'proposal' : proposal,
            'error_message' : "You didn't select a choice.",
        })
    else:
        ticket = ChoiceTicket(user=request.user, date_chosen=timezone.now(), proposal_choice=selected_choice)
        ticket.save()

        # make an entry in the current choice table for easy look up
        try:
            current_choice = CurrentChoiceTicket.objects.get(user = request.user, proposal = proposal)
        except (KeyError, CurrentChoiceTicket.DoesNotExist):
            current_choice = CurrentChoiceTicket(user = request.user, proposal = proposal, choice_ticket = ticket)
        else:
            current_choice.choice_ticket = ticket

        current_choice.save()
        return HttpResponseRedirect(reverse('list_proposals'))
