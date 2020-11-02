from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from consensus_engine.models import Proposal, ChoiceTicket, ProposalGroup, ConsensusHistory
from consensus_engine.utils import ProposalState
from consensus_engine.choice_templates import ChoiceTemplates


@method_decorator(login_required, name='dispatch')
class ProposalView(TemplateView):
    template_name = 'consensus_engine/view_proposal.html'

    def get_context_data(self, **kwargs):
        # view the proposal choices
        proposal = get_object_or_404(Proposal, pk=self.kwargs['proposal_id'])
        if 'query_date' in self.kwargs:
            query_date = self.kwargs['query_date']
        else:
            query_date = None
        current_choice = ChoiceTicket.objects.get_current_choice(user=self.request.user,
                                                                 proposal=proposal)
        active_choices = proposal.proposalchoice_set.activated()
        context = {'proposal': proposal, 'current_choice': current_choice,
                   'active_choices': active_choices, 'query_date': query_date,
                   'can_edit': proposal.user_can_edit(self.request.user)}
        try:
            vote_spread = proposal.get_voting_spread(query_date)
        except (KeyError, ConsensusHistory.DoesNotExist):
            context['error_message'] = 'No data for query date'
        else:
            context['vote_spread'] = vote_spread
            # get a list of previous months for history
            date_list = []
            if ConsensusHistory.objects.filter(proposal=proposal).count() > 0:
                earliest_history = ConsensusHistory.objects.earliest_snapshot(proposal)
                earliest_date = earliest_history.snapshot_date
                now = timezone.now()
                inc_date = earliest_date
                inc_year = earliest_date.year
                while True:
                    if inc_date.month == 12:
                        next_month = 1
                        inc_year += 1
                    else:
                        next_month = inc_date.month + 1
                    inc_date = inc_date.replace(day=1, month=next_month, year=inc_year,
                                                hour=0, minute=0, second=0, microsecond=0)
                    if inc_date >= now:
                        break
                    date_list.append(inc_date)
                if date_list != []:
                    context['history_date_list'] = date_list
        return context


@method_decorator(login_required, name='dispatch')
class CreateProposalView(CreateView):
    template_name = 'consensus_engine/new_proposal.html'
    model = Proposal
    fields = ['proposal_name', 'proposal_description']

    def form_valid(self, form):
        current_user = self.request.user
        if 'proposal_group_id' in self.kwargs:
            proposal_group = ProposalGroup.objects.get(pk=self.kwargs['proposal_group_id'])
            if not proposal_group.is_user_member(current_user):
                raise PermissionDenied("Adding a Proposal to a group you are not a member of is not allowed")
        else:
            proposal_group = None
        self.object = form.save(commit=False)
        self.object.owned_by = current_user
        self.object.date_proposed = timezone.now()
        self.object.proposal_group = proposal_group
        self.object.save()
        populate_option = int(self.request.POST["options"])
        population_types = [None,
                            ChoiceTemplates.genericMoscow,
                            ChoiceTemplates.genericYesNo,
                            ChoiceTemplates.generic1to5]
        self.object.populate_from_template(population_types[populate_option])
        self.object.determine_consensus()
        # save consensus history
        snapshot = ConsensusHistory.build_snapshot(self.object)
        snapshot.save()
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
    template_name = 'consensus_engine/list_my_proposals.html'

    def get_context_data(self, **kwargs):
        # view the proposal choices
        context = {}
        proposals_list = Proposal.objects.owned(self.request.user, states={ProposalState.DRAFT})
        context['draft_proposals_list'] = proposals_list
        proposals_list = Proposal.objects.owned(self.request.user, states={ProposalState.TRIAL})
        context['trial_proposals_list'] = proposals_list
        proposals_list = Proposal.objects.owned(self.request.user, states={ProposalState.PUBLISHED})
        context['published_proposals_list'] = proposals_list
        proposals_list = Proposal.objects.owned(self.request.user, states={ProposalState.ON_HOLD})
        context['on_hold_proposals_list'] = proposals_list
        proposals_list = Proposal.objects.owned(self.request.user, states={ProposalState.ARCHIVED})
        context['archived_proposals_list'] = proposals_list
        return context


@method_decorator(login_required, name='dispatch')
class ProposalListGroupView(ProposalListView):
    """ Sub class ProposalListView to get ones in group """
    template_name = 'consensus_engine/list_proposals.html'

    def get_context_data(self, **kwargs):
        # view the proposal choices
        proposal_group = get_object_or_404(ProposalGroup, pk=kwargs['proposal_group_id'])
        states = [ProposalState.PUBLISHED]
        if proposal_group.is_user_part_of_trial(self.request.user):
            states.append(ProposalState.TRIAL)
        proposals_list = Proposal.objects.in_group(proposal_group, states=states)
        can_edit = proposal_group.is_user_member(self.request.user)
        can_trial = proposal_group.is_user_part_of_trial(self.request.user)
        voting_enabled = can_edit
        context = {'proposals_list': proposals_list, 'proposal_group': proposal_group,
                   'can_edit': can_edit,
                   'can_create_proposals': can_edit and can_trial,
                   'can_invite': can_edit and can_trial, 'can_trial': can_trial,
                   'voting_enabled': voting_enabled}
        return context
