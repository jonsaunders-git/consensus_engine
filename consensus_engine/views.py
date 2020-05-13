from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse


from .models import Proposal, ProposalChoice, ChoiceTicket, ProposalGroup
from .forms import ProposalForm, ProposalChoiceForm, ProposalGroupForm

# Create your views here.

def index(request):
    return render(request, 'consensus_engine/index.html')



@login_required
def view_proposal(request, proposal_id):
    # view the proposal choices
    proposal = get_object_or_404(Proposal, pk=proposal_id)
    try:
        current_choice = ChoiceTicket.objects.get(user = request.user, proposal_choice__proposal = proposal, current = True)
    except (KeyError, ChoiceTicket.DoesNotExist):
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
def assign_proposals_group(request, proposal_id):
    proposal = get_object_or_404(Proposal, pk=proposal_id)

    if proposal.owned_by != request.user:
        return render(request, 'consensus_engine/edit_proposal.html', {
            'proposal' : proposal,
            'error_message' : "You don't have permissions to edit."
        })

    if request.method == 'POST':
        try:
            selected_group = ProposalGroup.objects.get(pk=request.POST['proposal_group'])
            proposal.proposal_group = selected_group
            proposal.save()
        except (KeyError, ProposalGroup.DoesNotExist):
            return render(request, 'consensus_engine/assign_proposals_group.html', {
                'proposal' : proposal,
                'error_message' : "You didn't select a choice.",
            })

        return HttpResponseRedirect('/proposals/')
    proposalgroup_list = ProposalGroup.objects.all
    context = {'proposalgroup_list': proposalgroup_list}
    return render(request, 'consensus_engine/assign_proposals_group.html', context)


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
def new_proposal(request):

    # get the proposal group - need to make is so that the default group
    #proposal_group = get_object_or_404(ProposalGroup, pk=proposal_group_id)

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
def new_proposal_in_group(request, proposal_group_id):

    # get the proposal group - need to make is so that the default group
    proposal_group = get_object_or_404(ProposalGroup, pk=proposal_group_id)

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
            obj.proposal_group = proposal_group
            obj.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProposalForm(initial={ 'date_proposed': timezone.now()})
    return render(request, 'consensus_engine/new_proposal.html', {'form': form, 'proposal_group' : proposal_group})


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
    proposals_list = Proposal.objects.my_votes(request.user)
    context = {'proposals_list': proposals_list}
    return render(request, 'consensus_engine/view_my_votes.html', context)

@login_required
def new_proposal_group(request):
     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProposalGroupForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # add a date_published
            obj = form.save(commit=False)
            obj.owned_by = request.user
            obj.save()
            # redirect to a new URL:
        return HttpResponseRedirect('/proposalgroups/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProposalGroupForm()
    return render(request, 'consensus_engine/new_proposal_group.html', {'form': form})


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

@login_required
def edit_proposal_group(request, proposal_group_id):
    # view the proposal choices
    proposal_group = get_object_or_404(ProposalGroup, pk=proposal_group_id)

     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProposalGroupForm(request.POST, instance=proposal_group)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...

            # add a date_published - really we need to just make a new version...
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/proposalgroups/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProposalGroupForm(instance=proposal_group)

    return render(request, 'consensus_engine/edit_proposal_group.html', {'form': form})

def uiformat(request):
    return render(request, 'consensus_engine/uiformat.html')
