from django import template
from consensus_engine.models import ProposalGroup, ProposalChoice, Proposal
from consensus_engine.models import GroupInvite
from django.contrib.auth.models import User

register = template.Library()


@register.inclusion_tag('consensus_engine/visible_groups.html')
def visible_groups(user):
    visible_groups = ProposalGroup.objects.groups_for_member(user).order_by('group_name')
    return {'visible_groups': visible_groups}


# this needs refactoring as it calls multiple times per view...
@register.inclusion_tag('consensus_engine/total_votes.html')
def total_votes(proposal_id):
    proposal = Proposal.objects.get(pk=proposal_id)
    return {'total_votes': proposal.get_total_votes()}


# this needs refactoring as it calls multiple times per view...
@register.inclusion_tag('consensus_engine/current_consensus.html')
def current_consensus(proposal_id):
    try:
        consensus_consensus = (ProposalChoice.objects.get(deactivated_date__isnull=True,
                                                          proposal__id=proposal_id,
                                                          current_consensus=True)
                                                     .text)
    except ProposalChoice.DoesNotExist:
        consensus_consensus = "No consensus"
    return {'current_consensus': consensus_consensus}


# this needs refactoring as it calls multiple times per view...
@register.inclusion_tag('consensus_engine/my_vote.html')
def my_vote(proposal_id, user_id):
    proposal = Proposal.objects.get(pk=proposal_id)
    try:
        my_vote = (ProposalChoice.objects.get(deactivated_date__isnull=True,
                                              proposal__id=proposal_id,
                                              choiceticket__user_id=user_id,
                                              choiceticket__current=True,
                                              choiceticket__state=proposal.state)
                                         .text)
    except ProposalChoice.DoesNotExist:
        my_vote = "None"
    return {'my_vote': my_vote}


@register.inclusion_tag('consensus_engine/my_open_invites_count.html')
def my_open_invites_count(user):
    open_invites_count = GroupInvite.objects.my_open_invites_count(user)
    return {'open_invites_count': open_invites_count}


@register.inclusion_tag('consensus_engine/release_notes.html')
def release_notes():
    # added this in so I can remove it easily and put multiple release notes in, in the future
    return {}


@register.inclusion_tag('consensus_engine/user_search.html')
def user_search():
    users = User.objects.all
    return {'users': users}


@register.inclusion_tag('consensus_engine/proposal_state.html')
def proposal_state(proposal):
    return {'proposal_state': proposal.current_state.name}


@register.inclusion_tag('consensus_engine/proposal_list_element.html')
def proposal_list_element(proposal, current_user_id, vote_enabled='', next=''):
    return {'proposal': proposal, 'current_user_id': current_user_id, 'vote_enabled': vote_enabled, 'next': next}
