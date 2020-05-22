from django.views import View
from django.views.generic.base import TemplateView

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from consensus_engine.models import ChoiceTicket


@method_decorator(login_required, name='dispatch')
class MyVotesView(TemplateView):
    """ Shows a list of proposals """
    template_name = 'consensus_engine/view_my_votes.html'

    def get_context_data(self, **kwargs):
        votes_list = ChoiceTicket.objects.my_votes(self.request.user)
        context = {'votes_list': votes_list}
        return context
