from django.urls import path
from django.urls import include, re_path, register_converter
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from consensus_engine.converters import DateConverter

from . import views

register_converter(DateConverter, 'date')

urlpatterns = [
    path('', login_required(
         TemplateView.as_view(template_name="consensus_engine/index.html")),
         name='index'),
    path('proposals/new/',
         views.PickProposalGroupView.as_view(), name='new_proposal'),
    path('votes/owned/',
         views.MyVotesView.as_view(), name='view_my_votes'),
    path('invites/',
         views.InvitesView.as_view(), name='view_invites'),
    path('proposals/owned/',
         views.ProposalListView.as_view(), name="my_proposals"),
    path('proposals/<int:proposal_id>/',
         views.ProposalView.as_view(), name='view_proposal'),
    path('proposals/<int:proposal_id>/<date:query_date>/',
         views.ProposalView.as_view(), name='view_proposal_at_date'),
    path('proposals/<int:pk>/edit/',
         views.EditProposalView.as_view(), name='edit_proposal'),
    path('proposals/<int:proposal_id>/assign/group/',
         views.PickProposalGroupView.as_view(), name='assign_proposals_group'),
    path('proposals/<int:proposal_id>/vote/',
         views.VoteView.as_view(), name='vote_proposal'),
    path('proposals/<int:proposal_id>/change_state/',
         views.StateView.as_view(), name='change_state'),
    path('invite/<int:invite_id>/',
         views.InviteView.as_view(), name='accept_invite'),
    path('proposals/<int:proposal_id>/choice/new/',
         views.CreateProposalChoiceView.as_view(), name='new_choice'),
    path('proposals/<int:proposal_id>/choice/<int:pk>/edit/',
         views.EditProposalChoiceView.as_view(), name='edit_choice'),
    path('proposals/<int:proposal_id>/choice/<int:pk>/delete/',
         views.DeleteProposalChoiceView.as_view(), name='delete_choice'),
    path('proposalgroups/new/',
         views.CreateProposalGroupView.as_view(), name='new_proposal_group'),
    path('proposalgroups/',
         views.ProposalGroupListView.as_view(), name='list_proposal_groups'),
    path('proposalgroups/owned/',
         views.MyProposalGroupListView.as_view(), name='my_proposal_groups'),
    path('proposalgroups/<int:pk>/edit/',
         views.EditProposalGroupView.as_view(), name='edit_proposal_group'),
    path('proposalgroups/<int:pk>/invite/',
         views.InvitePersonView.as_view(), name='invite_people'),
    path('proposalgroups/<int:proposal_group_id>/proposals/',
         views.ProposalListGroupView.as_view(), name='group_proposals'),
    path('proposalgroups/<int:proposal_group_id>/members/',
         views.ProposalGroupMemberListView.as_view(), name='list_group_members'),
    path('groupmembership/<int:pk>/delete/',
         views.RemoveGroupMemberView.as_view(), name='remove_group_member'),
    path('groupmembership/<int:pk>/edit/',
         views.EditGroupMembershipView.as_view(), name='edit_group_membership'),
    path('proposalgroups/<int:proposal_group_id>/join/',
         views.JoinProposalGroupMembersView.as_view(), name='join_group_members'),
    path('proposalgroups/<int:proposal_group_id>/proposals/new/',
         views.CreateProposalView.as_view(), name='new_proposal_in_group'),
    path('accounts/', include('django.contrib.auth.urls')),
    re_path(r'^login/$', views.RememberMeLoginView.as_view(), name="login"),
    path('uiformat/', views.uiformat, name="uiformat"),  # just for testing UI stuff - to be removed
]

urlpatterns += staticfiles_urlpatterns()
