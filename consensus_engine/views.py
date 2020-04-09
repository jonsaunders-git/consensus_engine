from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from .models import Proposal

# Create your views here.

def index(request):
    return render(request, 'consensus_engine/index.html')

@login_required
def view_proposal(request, proposal_id):
    return HttpResponse("You're looking at the view proposal page.")

@login_required
def new_proposal(request):
    return HttpResponse("You're looking at the enter proposal page.")

@login_required
def list_proposals(request):
    proposals_list = Proposal.objects.order_by('-date_proposed')[:5]
    context = {'proposals_list': proposals_list}
    return render(request, 'consensus_engine/list_proposals.html', context)
