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

from consensus_engine.models import Proposal, ChoiceTicket, ProposalGroup



@method_decorator(login_required, name='dispatch')
class CreateProposalGroupView(CreateView):
    template_name = 'consensus_engine/new_proposal_group.html'
    model = ProposalGroup
    fields = ['group_name', 'group_description']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owned_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class EditProposalGroupView(UpdateView):
    template_name = 'consensus_engine/edit_proposal_group.html'
    model = ProposalGroup
    fields = ['group_name', 'group_description']
