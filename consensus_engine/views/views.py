from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.utils import timezone


from consensus_engine.models import Proposal, ProposalChoice, ChoiceTicket, ProposalGroup
from consensus_engine.forms import ProposalForm, ProposalChoiceForm, ProposalGroupForm

# Create your views here.

@login_required
def vote_proposal(request, proposal_id):
    # view the proposal choices
    proposal = get_object_or_404(Proposal, pk=proposal_id)

    if request.method == 'POST':
        try:
            selected_choice = proposal.proposalchoice_set.get(pk=request.POST['choice'])
            selected_choice.vote(request.user)
        except (KeyError, ProposalChoice.DoesNotExist):
            return render(request, 'consensus_engine/vote_proposal.html', {
                'proposal' : proposal,
                'error_message' : "You didn't select a choice.",
            })
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

    try:
        # should be just the one.
        current_choice = ChoiceTicket.objects.get(user = request.user, proposal_choice__proposal = proposal, current=True)
    except (KeyError, ChoiceTicket.DoesNotExist):
        current_choice = None

    active_choices = proposal.proposalchoice_set.activated()

    context = {'proposal' : proposal, 'current_choice' : current_choice, 'active_choices' : active_choices }
    return render(request, 'consensus_engine/vote_proposal.html', context)

@login_required
def my_proposals(request):
    proposals_list = Proposal.objects.owned(request.user)
    context = {'proposals_list': proposals_list}
    return render(request, 'consensus_engine/list_proposals.html', context)

@login_required
def group_proposals(request, proposal_group_id):
    proposal_group = get_object_or_404(ProposalGroup, pk=proposal_group_id)
    proposals_list = Proposal.objects.in_group(proposal_group)
    context = {'proposals_list': proposals_list, 'proposal_group': proposal_group }
    return render(request, 'consensus_engine/list_proposals.html', context)

@login_required
def view_my_votes(request):
    votes_list = ChoiceTicket.objects.my_votes(request.user)
    context = {'votes_list': votes_list}
    return render(request, 'consensus_engine/view_my_votes.html', context)

@login_required
def list_proposal_groups(request):
    proposalgroup_list = ProposalGroup.objects.all
    context = {'proposalgroup_list': proposalgroup_list}
    return render(request, 'consensus_engine/list_proposal_groups.html', context)

@login_required
def my_proposal_groups(request):
    proposalgroup_list = ProposalGroup.objects.owned(request.user).order_by('group_name')
    context = {'proposalgroup_list': proposalgroup_list}
    return render(request, 'consensus_engine/list_proposal_groups.html', context)


def uiformat(request):
    return render(request, 'consensus_engine/uiformat.html')
