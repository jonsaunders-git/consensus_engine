from django.shortcuts import render

# Create your views here.


def uiformat(request): # pragma: no cover
    return render(request, 'consensus_engine/uiformat.html')
