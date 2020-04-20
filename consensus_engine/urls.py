from django.urls import path
from django.urls import include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('proposals/new/', views.new_proposal, name='new_proposal'),
    path('proposals/', views.list_proposals, name='list_proposals'),
    path('proposals/<int:proposal_id>/', views.view_proposal, name='view_proposal'),
    path('proposals/vote/<int:proposal_id>/', views.vote_proposal, name='vote_proposal'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('<int:proposal_id>/register_vote/', views.register_vote, name='register_vote'),
]
