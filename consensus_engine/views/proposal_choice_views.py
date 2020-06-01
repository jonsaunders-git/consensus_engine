from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

from consensus_engine.models import Proposal, ChoiceTicket, ProposalGroup, ProposalChoice

@method_decorator(login_required, name='dispatch')
class CreateProposalChoiceView(CreateView):
    template_name = 'consensus_engine/new_choice.html'
    model = ProposalChoice
    fields = ['text', 'priority']

    def form_valid(self, form):
        proposal = Proposal.objects.get(pk=self.kwargs['proposal_id'])
        if proposal.user_can_edit(self.request.user):
            self.object = form.save(commit=False)
            self.object.proposal = proposal
            self.object.activated_date = timezone.now()
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            raise PermissionDenied('Editing is not allowed')

    def get_context_data(self, **kwargs):
        # add the proposal_group to the context of it exists
        context = super().get_context_data(**kwargs)
        if 'proposal_id' in self.kwargs:
            proposal_id = Proposal.objects.get(pk=self.kwargs['proposal_id']).id
            context['proposal_id'] = proposal_id
        return context


@method_decorator(login_required, name='dispatch')
class EditProposalChoiceView(UpdateView):
    template_name = 'consensus_engine/edit_choice.html'
    model = ProposalChoice
    fields = ['text', 'priority']

    def form_valid(self, form):
        if self.object.proposal.user_can_edit(self.request.user):
            return super().form_valid(form)
        else:
            raise PermissionDenied("Editing is not allowed")


@method_decorator(login_required, name='dispatch')
class DeleteProposalChoiceView(DeleteView):
  model = ProposalChoice
  template_name = 'consensus_engine/delete_choice.html'

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    if not self.object.proposal.user_can_edit(self.request.user):
        raise PermissionDenied("Editing is not allowed")
    self.success_url = reverse('view_proposal', args=[self.object.proposal.id])
    if 'okay_btn' in request.POST:
        self.object.deactivated_date = timezone.now()
        self.object.save()
    return HttpResponseRedirect(self.get_success_url())
