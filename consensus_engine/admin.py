from django.contrib import admin

from .models import Proposal, ProposalChoice, ChoiceTicket, CurrentChoiceTicket

# Register your models here.

admin.site.register(Proposal)
admin.site.register(ProposalChoice)
admin.site.register(ChoiceTicket)
admin.site.register(CurrentChoiceTicket)
