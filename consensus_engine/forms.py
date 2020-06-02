from django.forms import ModelForm, BooleanField
from django.contrib.auth.forms import AuthenticationForm

from .models import Proposal, ProposalChoice, ProposalGroup


class RememberMeLoginForm(AuthenticationForm):
    #  add the remember_me field
    remember_me = BooleanField(required=False, initial=True)


class ProposalForm(ModelForm):
    class Meta:
        model = Proposal
        fields = ['proposal_name', 'proposal_description']


class ProposalChoiceForm(ModelForm):
    class Meta:
        model = ProposalChoice
        fields = ['text', 'priority']


class ProposalGroupForm(ModelForm):
    class Meta:
        model = ProposalGroup
        fields = ['group_name', 'group_description']
