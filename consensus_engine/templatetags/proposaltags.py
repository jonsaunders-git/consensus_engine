from django import template
from consensus_engine.models import ProposalGroup

register = template.Library()

@register.inclusion_tag('consensus_engine/visible_groups.html')
def visible_groups(user):
    visible_groups = ProposalGroup.objects.owned(user)
    return {'visible_groups': visible_groups}
