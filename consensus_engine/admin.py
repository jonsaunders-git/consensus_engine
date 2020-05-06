from django.contrib import admin

from .models import Proposal, ProposalChoice, ChoiceTicket

# Register your models here.

admin.site.register(Proposal)
admin.site.register(ProposalChoice)
admin.site.register(ChoiceTicket)
