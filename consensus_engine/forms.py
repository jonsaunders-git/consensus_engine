from django.forms import ModelForm, Textarea
from .models import Proposal, ProposalChoice, ProposalGroup


class ProposalForm(ModelForm):
    class Meta:
        model = Proposal
        fields = ['proposal_name', 'proposal_caption']
        widgets = {
            'proposal_caption': Textarea(attrs={'cols': 80, 'rows': 20}),
        }


class ProposalChoiceForm(ModelForm):
    class Meta:
        model = ProposalChoice
        fields = ['text', 'priority']

class ProposalGroupForm(ModelForm):
    class Meta:
        model = ProposalGroup
        fields = ['group_name']
