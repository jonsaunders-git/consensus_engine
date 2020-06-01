from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from consensus_engine.models import Proposal, ChoiceTicket, ProposalGroup, GroupMembership

@method_decorator(login_required, name='dispatch')
class CreateProposalGroupView(CreateView):
    template_name = 'consensus_engine/new_proposal_group.html'
    model = ProposalGroup
    fields = ['group_name', 'group_description']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owned_by = self.request.user
        self.object.save()
        # add the owner as the first member
        member = GroupMembership(user=self.request.user, group=self.object, date_joined=timezone.now())
        member.save()
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class EditProposalGroupView(UpdateView):
    template_name = 'consensus_engine/edit_proposal_group.html'
    model = ProposalGroup
    fields = ['group_name', 'group_description']


@method_decorator(login_required, name='dispatch')
class PickProposalGroupView(TemplateView):
    """ Class based view for picking a Proposal Group """
    template_name = 'consensus_engine/pick_proposal_group.html'

    def get_context_data(self, **kwargs):
        proposalgroup_list = ProposalGroup.objects.all
        context = {'proposalgroup_list': proposalgroup_list, 'current_group_id' : 0}
        if 'proposal_id' in kwargs:
            proposal = get_object_or_404(Proposal, pk=kwargs['proposal_id'])
            if proposal.proposal_group is not None:
                context['current_group_id'] = proposal.proposal_group.id
            if proposal.owned_by != self.request.user:
                context.update({
                    'error_message' : "You don't have permissions to edit the group."
                })
        return context

    def post(self, request, **kwargs):
        if 'proposal_id' in kwargs:
            proposal = get_object_or_404(Proposal, pk=kwargs['proposal_id'])
            success_url = reverse('view_proposal', args=[proposal.id])
            if proposal.owned_by != request.user:
                return render(request, 'consensus_engine/edit_proposal.html', {
                    'proposal' : proposal,
                    'error_message' : "You don't have permissions for this activity."
                })
            try:
                selected_group = ProposalGroup.objects.get(pk=request.POST['proposal_group'])
                proposal.proposal_group = selected_group
                proposal.save()
            except (KeyError, ProposalGroup.DoesNotExist):
                return render(request, 'consensus_engine/pick_proposal_group.html', {
                    'proposal' : proposal,
                    'error_message' : "You didn't select a choice.",
                })
        else:
            selected_group = ProposalGroup.objects.get(pk=request.POST['proposal_group'])
            success_url = reverse('new_proposal_in_group', args=[selected_group.id])

        return HttpResponseRedirect(success_url)


@method_decorator(login_required, name='dispatch')
class ProposalGroupListView(TemplateView):
    """ Shows a list of proposal groups """
    template_name = 'consensus_engine/list_proposal_groups.html'

    def get_group_membership_list(self, user):
        return ProposalGroup.objects.list_of_membership(user)

    def get_proposal_group_list(self):
        return ProposalGroup.objects.all()

    def get_context_data(self, **kwargs):
        # view the proposal choices
        proposalgroups_list = self.get_proposal_group_list()
        membership_list = self.get_group_membership_list(self.request.user)
        context = {'proposalgroup_list': proposalgroups_list, 'membership_list' : membership_list}
        return context


@method_decorator(login_required, name='dispatch')
class MyProposalGroupListView(ProposalGroupListView):
    """ Shows a list of proposal groups owned by the current user """
    template_name = 'consensus_engine/list_proposal_groups.html'

    def get_proposal_group_list(self):
        return ProposalGroup.objects.owned(self.request.user).order_by('group_name')


@method_decorator(login_required, name='dispatch')
class JoinProposalGroupMembersView(TemplateView):
    """ Shows a simple dialog to add user to group member ship """
    template_name = 'consensus_engine/join_group_members.html'

    def get_context_data(self, **kwargs):
        proposalgroup = get_object_or_404(ProposalGroup, pk=kwargs['proposal_group_id'])
        context = {'proposalgroup' : proposalgroup}
        return context

    def post(self, request, **kwargs):
        proposalgroup = get_object_or_404(ProposalGroup, pk=kwargs['proposal_group_id'])
        success_url = reverse('group_proposals', args=[proposalgroup.id])
        proposalgroup.join_group(request.user)
        return HttpResponseRedirect(success_url)
