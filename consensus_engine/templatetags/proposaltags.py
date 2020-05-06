from django import template
from django.db import models
from consensus_engine.models import ProposalGroup, Proposal, ChoiceTicket, ProposalChoice

register = template.Library()

@register.inclusion_tag('consensus_engine/visible_groups.html')
def visible_groups(user):
    visible_groups = ProposalGroup.objects.owned(user).order_by('group_name')
    return {'visible_groups': visible_groups}


# this needs refactoring as it calls multiple times per view...
@register.inclusion_tag('consensus_engine/total_votes.html')
def total_votes(proposal_id):
    total_votes = ChoiceTicket.objects.filter(proposal_choice__proposal__id=proposal_id, current=1).count()
    return {'total_votes': total_votes}

# this needs refactoring as it calls multiple times per view...
@register.inclusion_tag('consensus_engine/my_vote.html')
def my_vote(proposal_id, user_id):
    try:
        my_vote = ProposalChoice.objects.get(proposal__id=proposal_id, choiceticket__user_id=user_id, choiceticket__current=True).text
    except:
        my_vote = "None"
    return {'my_vote': my_vote }
