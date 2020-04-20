from django.forms import ModelForm, Textarea
from .models import Proposal

class ProposalForm(ModelForm):
    class Meta:
        model = Proposal
        fields = ['proposal_name', 'proposal_caption']
        widgets = {
            'proposal_caption': Textarea(attrs={'cols': 80, 'rows': 20}),
        }
