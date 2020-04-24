from django.urls import path
from django.urls import include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('proposals/new/', views.new_proposal, name='new_proposal'),
    path('proposals/', views.list_proposals, name='list_proposals'),
    path('votes/owned/', views.view_my_votes, name='view_my_votes'),
    path('proposals/owned/', views.my_proposals, name='my_proposals'),
    path('proposals/<int:proposal_id>/', views.view_proposal, name='view_proposal'),
    path('proposals/<int:proposal_id>/edit/', views.edit_proposal, name='edit_proposal'),
    path('proposals/<int:proposal_id>/assign/group/', views.assign_proposals_group, name='assign_proposals_group'),
    path('proposals/<int:proposal_id>/vote/', views.vote_proposal, name='vote_proposal'),
    path('proposals/<int:proposal_id>/choice/new/', views.new_choice, name='new_choice'),
    path('proposals/<int:proposal_id>/choice/<int:choice_id>/edit/', views.edit_choice, name='edit_choice'),
    path('proposals/<int:proposal_id>/choice/<int:choice_id>/delete/', views.delete_choice, name='delete_choice'),
    path('proposalgroups/new/', views.new_proposal_group, name='new_proposal_group'),
    path('proposalgroups/', views.list_proposal_groups, name='list_proposal_groups'),
    path('proposalgroups/owned/', views.my_proposal_groups, name='my_proposal_groups'),
    path('proposalgroups/<int:proposal_group_id>/edit/', views.edit_proposal_group, name='edit_proposal_group'),
    path('proposalgroups/<int:proposal_group_id>/proposals/', views.group_proposals, name='group_proposals'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('<int:proposal_id>/register_vote/', views.register_vote, name='register_vote'),
]
