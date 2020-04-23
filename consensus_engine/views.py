from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse

from .models import Proposal, ProposalChoice, ChoiceTicket, CurrentChoiceTicket
from .forms import ProposalForm, ProposalChoiceForm

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
        current_choice = None

    active_choices = proposal.proposalchoice_set.activated()

    context = {'proposal' : proposal, 'current_choice' : current_choice, 'active_choices' : active_choices }
    return render(request, 'consensus_engine/view_proposal.html', context)


@login_required
def edit_proposal(request, proposal_id):
    # view the proposal choices
    proposal = get_object_or_404(Proposal, pk=proposal_id)

    if proposal.owned_by != request.user:
        return render(request, 'consensus_engine/edit_proposal.html', {
            'proposal' : proposal,
            'error_message' : "You don't have permissions to edit."
        })

     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProposalForm(request.POST, instance=proposal)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            # add a date_published - really we need to just make a new version...

            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/proposals/')


    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProposalForm(instance=proposal)

    return render(request, 'consensus_engine/edit_proposal.html', {'form': form})


@login_required
def vote_proposal(request, proposal_id):
    # view the proposal choices
    proposal = get_object_or_404(Proposal, pk=proposal_id)
    try:
        current_choice = CurrentChoiceTicket.objects.get(user = request.user, proposal = proposal)
    except (KeyError, CurrentChoiceTicket.DoesNotExist):
        current_choice = None

    active_choices = proposal.proposalchoice_set.activated()

    context = {'proposal' : proposal, 'current_choice' : current_choice, 'active_choices' : active_choices }
    return render(request, 'consensus_engine/list_proposal_choices.html', context)


@login_required
def new_proposal(request):
     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProposalForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            # add a date_published
            obj = form.save(commit=False)
            obj.date_proposed = timezone.now()
            obj.owned_by = request.user
            obj.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/proposals/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProposalForm(initial={'date_proposed': timezone.now()})
    return render(request, 'consensus_engine/new_proposal.html', {'form': form})


@login_required
def new_choice(request, proposal_id):
    proposal = get_object_or_404(Proposal, pk=proposal_id)

    if proposal.owned_by != request.user:
        return render(request, 'consensus_engine/new_proposal.html', {
            'proposal' : proposal,
            'error_message' : "You don't have permissions to edit."
        })

     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProposalChoiceForm(request.POST)
        form.instance.proposal = proposal
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            obj = form.save(commit=False)
            obj.activated_date = timezone.now()
            obj.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/proposals/%d/' % proposal_id)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProposalChoiceForm()
    return render(request, 'consensus_engine/new_choice.html', {'form': form, 'proposal_id' : proposal_id})


@login_required
def edit_choice(request, proposal_id, choice_id):

    choice = get_object_or_404(ProposalChoice, pk=choice_id)

    if choice.proposal.owned_by != request.user:
        return render(request, 'consensus_engine/edit_choice.html', {
            'proposal' : choice.proposal,
            'error_message' : "You don't have permissions to edit."
        })

     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProposalChoiceForm(request.POST, instance=choice)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/proposals/%d/' % proposal_id)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProposalChoiceForm(instance=choice)

    return render(request, 'consensus_engine/edit_choice.html', {'form': form})


@login_required
def delete_choice(request, proposal_id, choice_id):
    choice = get_object_or_404(ProposalChoice, pk=choice_id)

    if choice.proposal.owned_by != request.user:
        return render(request, 'consensus_engine/delete_proposal.html', {
            'proposal' : choice.proposal,
            'error_message' : "You don't have permissions to edit."
        })
     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        # check whether it's valid:
        if 'okay_btn' in request.POST:
            # process the data in form.cleaned_data as required
            # ...
            choice.deactivated_date = timezone.now()
            choice.save()
        # redirect to a new URL:
        return HttpResponseRedirect('/proposals/%d/' % proposal_id)

    return render(request, 'consensus_engine/delete_choice.html')


@login_required
def list_proposals(request):
    proposals_list = Proposal.objects.activated()
    context = {'proposals_list': proposals_list}
    return render(request, 'consensus_engine/list_proposals.html', context)


@login_required
def my_proposals(request):
    proposals_list = Proposal.objects.owned(request.user)
    context = {'proposals_list': proposals_list}
    return render(request, 'consensus_engine/list_proposals.html', context)

@login_required
def view_my_votes(request):
    proposals_list = Proposal.objects.myvotes(request.user)
    context = {'proposals_list': proposals_list}
    return render(request, 'consensus_engine/view_my_votes.html', context)

@login_required
def register_vote(request, proposal_id):
    proposal = get_object_or_404(Proposal, pk=proposal_id)
    try:
        selected_choice = proposal.proposalchoice_set.get(pk=request.POST['choice'])
        vote(request.user, proposal, selected_choice)
    except (KeyError, ProposalChoice.DoesNotExist):
        return render(request, 'consensus_engine/list_proposal_choices.html', {
            'proposal' : proposal,
            'error_message' : "You didn't select a choice.",
        })
    next = request.POST.get('next', '/')
    print(next)
    return HttpResponseRedirect(next)

def vote(user, proposal, selected_choice):
    ticket = ChoiceTicket(user=user, date_chosen=timezone.now(), proposal_choice=selected_choice)
    ticket.save()
    # make an entry in the current choice table for easy look up
    try:
        current_choice = CurrentChoiceTicket.objects.get(user = user, proposal = proposal)
    except (KeyError, CurrentChoiceTicket.DoesNotExist):
        current_choice = CurrentChoiceTicket(user = user, proposal = proposal, choice_ticket = ticket)
    else:
        current_choice.choice_ticket = ticket

    current_choice.save()
