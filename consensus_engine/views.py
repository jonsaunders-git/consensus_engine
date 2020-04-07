from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, 'consensus_engine/index.html')


def new_proposal(request):
    return HttpResponse("You're looking at the enter proposal page.")

def list_proposals(request):
    return HttpResponse("You're looking at the list proposals page.")
