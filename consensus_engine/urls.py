from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('proposals/new/', views.new_proposal, name='new_proposal'),
    path('proposals/', views.list_proposals, name='list_proposals'),
]
