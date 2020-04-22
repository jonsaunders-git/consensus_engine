from django.urls import path
from django.urls import include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('proposals/new/', views.new_proposal, name='new_proposal'),
    path('proposals/', views.list_proposals, name='list_proposals'),
    path('proposals/<int:proposal_id>/', views.view_proposal, name='view_proposal'),
    path('proposals/<int:proposal_id>/edit/', views.edit_proposal, name='edit_proposal'),
    path('proposals/<int:proposal_id>/vote/', views.vote_proposal, name='vote_proposal'),
    path('proposals/<int:proposal_id>/choice/new/', views.new_choice, name='new_choice'),
    path('proposals/<int:proposal_id>/choice/<int:choice_id>/edit/', views.edit_choice, name='edit_choice'),
    path('proposals/<int:proposal_id>/choice/<int:choice_id>/delete/', views.delete_choice, name='delete_choice'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('<int:proposal_id>/register_vote/', views.register_vote, name='register_vote'),
]
