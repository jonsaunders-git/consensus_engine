from django.forms import ModelForm, Textarea, BooleanField
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from .models import Proposal, ProposalChoice, ProposalGroup


class RememberMeLoginForm(AuthenticationForm):
    remember_me = BooleanField(required=False, initial=True)  # and add the remember_me field

class ProposalForm(ModelForm):
    class Meta:
        model = Proposal
        fields = ['proposal_name', 'proposal_description']
        widgets = {
            'proposal_description': Textarea(attrs={'cols': 80, 'rows': 20}),
        }


class ProposalChoiceForm(ModelForm):
    class Meta:
        model = ProposalChoice
        fields = ['text', 'priority']

class ProposalGroupForm(ModelForm):
    class Meta:
        model = ProposalGroup
        fields = ['group_name', 'group_description']
