from django.urls import path
from django.urls import include, re_path
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    path('', login_required(TemplateView.as_view(template_name="consensus_engine/index.html")), name='index'),
    path('proposals/new/', views.CreateProposalView.as_view(), name='new_proposal'),
    path('votes/owned/', views.view_my_votes, name='view_my_votes'),
    path('proposals/', views.my_proposals, name="proposals"),
    path('proposals/owned/', views.my_proposals, name='my_proposals'),
    path('proposals/<int:proposal_id>/', views.ProposalView.as_view(), name='view_proposal'),
    path('proposals/<int:pk>/edit/', views.EditProposalView.as_view(), name='edit_proposal'),
    path('proposals/<int:proposal_id>/assign/group/', views.assign_proposals_group, name='assign_proposals_group'),
    path('proposals/<int:proposal_id>/vote/', views.vote_proposal, name='vote_proposal'),
    path('proposals/<int:proposal_id>/choice/new/', views.CreateProposalChoiceView.as_view(), name='new_choice'),
    path('proposals/<int:proposal_id>/choice/<int:pk>/edit/', views.EditProposalChoiceView.as_view(), name='edit_choice'),
    path('proposals/<int:proposal_id>/choice/<int:pk>/delete/', views.DeleteProposalChoiceView.as_view(), name='delete_choice'),
    path('proposalgroups/new/', views.CreateProposalGroupView.as_view(), name='new_proposal_group'),
    path('proposalgroups/', views.list_proposal_groups, name='list_proposal_groups'),
    path('proposalgroups/owned/', views.my_proposal_groups, name='my_proposal_groups'),
    path('proposalgroups/<int:pk>/edit/', views.EditProposalGroupView.as_view(), name='edit_proposal_group'),
    path('proposalgroups/<int:proposal_group_id>/proposals/', views.group_proposals, name='group_proposals'),
    path('proposalgroups/<int:proposal_group_id>/proposals/new/', views.CreateProposalView.as_view(), name='new_proposal_in_group'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('uiformat/', views.uiformat, name="uiformat"),
    re_path(r'^login/$', views.RememberMeLoginView.as_view(), name="login"),

]
