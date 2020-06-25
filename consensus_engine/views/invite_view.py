from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404
from django.db import DataError

from consensus_engine.models import GroupInvite, ProposalGroup


@method_decorator(login_required, name='dispatch')
class InvitesView(TemplateView):
    """ Shows a list of invites """
    template_name = 'consensus_engine/view_invites.html'

    def get_context_data(self, **kwargs):
        invites = GroupInvite.objects.my_open_invites(self.request.user)
        context = {'invites_list': invites}
        return context


@method_decorator(login_required, name='dispatch')
class InviteView(TemplateView):
    """ Class based view for showing invites """
    template_name = 'consensus_engine/accept_invite.html'

    def get_context_data(self, **kwargs):
        invite = get_object_or_404(GroupInvite, pk=kwargs['invite_id'])
        context = {'invite': invite}
        return context

    def post(self, request, **kwargs):
        invite = get_object_or_404(GroupInvite, pk=kwargs['invite_id'])
        if 'accept_btn' in self.request.POST:
            invite.accept()
        else:
            invite.decline()
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


@method_decorator(login_required, name='dispatch')
class InvitePersonView(TemplateView):
    """ Class based view for inviting other people to a group """
    template_name = 'consensus_engine/invite_person.html'

    def get_context_data(self, **kwargs):
        group = get_object_or_404(ProposalGroup, pk=kwargs['pk'])
        context = {'group': group}
        return context

    def post(self, request, **kwargs):
        group = get_object_or_404(ProposalGroup, pk=kwargs['pk'])
        selected_user = User.objects.get(pk=request.POST['user_id'])
        try:
            group.invite_user(inviter_user=self.request.user, invitee_user=selected_user)
        except DataError as e:
            return render(request, 'consensus_engine/invite_person.html', {
                'error_message': str(e),
            })
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
