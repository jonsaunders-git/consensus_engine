from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User
from consensus_engine.models import Proposal, ProposalChoice, ChoiceTicket, ProposalGroup, GroupMembership
from django.test import TestCase
from django.utils import timezone
from django.contrib.sessions.middleware import SessionMiddleware
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView


class OneUserMixin(object):
    def setUp(self):
        # Every test needs access to the request factory.
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')


class TwoUserMixin(OneUserMixin):
    def setUp(self):
        # Every test needs access to the request factory.
        OneUserMixin.setUp(self)
        self.user2 = User.objects.create_user(username='jacob2',
                                              email='jacob@…',
                                              password='top_secret')


class ProposalGroupMixin(object):
    # needs to be used inconjunction with a UserMixin or it won't work

    def create_proposal_group(self, group_name="test group",
                              owned_by=None,
                              group_description="it's only a test group"):
        if owned_by==None:
            owned_by = self.user
        pg = ProposalGroup.objects.create(group_name=group_name,
                                          owned_by=owned_by,
                                          group_description=group_description)
        pg.join_group(owned_by)
        return pg


class ProposalMixin(object):
    # needs to be used inconjunction with a UserMixin or it won't work
    def create_new_proposal(self, proposal_name="only a test",
                            date_proposed=timezone.now(),
                            proposal_description="yes, this is only a test",
                            proposal_group=None, owned_by=None):
        if owned_by==None:
            owned_by = self.user
        return Proposal.objects.create(proposal_name=proposal_name,
                                       date_proposed=date_proposed,
                                       proposal_description=proposal_description,
                                       owned_by=owned_by,
                                       proposal_group=proposal_group)

    def create_proposal_with_two_proposal_choices(self,
            proposal_name="only a test", date_proposed=timezone.now(),
            proposal_description="yes, this is only a test", proposal_group=None, owned_by=None,
            proposal_choice_1_name="Yes", proposal_choice_2_name="No"):
        p = self.create_new_proposal(proposal_name, date_proposed, proposal_description, proposal_group, owned_by)
        pc1 = ProposalChoice.objects.create(proposal=p, text=proposal_choice_1_name,
            priority=100, activated_date=timezone.now())
        pc2 = ProposalChoice.objects.create(proposal=p, text=proposal_choice_2_name,
            priority=200, activated_date=timezone.now())
        return p


class ViewMixin(object):
    path = None
    form = None
    view = None
    current_user = None

    def get_form(self, form_class=None, data=None):
        if form_class is None:
            form_class = self.form
        return form_class(data=data)

    def get_view(self, view_class=None, kwargs={}):
        if view_class is None:
            view_class = self.view
        vc = view_class()
        vc.kwargs = kwargs
        return vc

    def getSessionRequest(self, path=None):
        if path is None:
            path = self.path
        request = self.factory.get(path)
        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        if self.current_user is None:
            self.current_user = self.user
        request.user = self.current_user

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        return request

    def getValidView(self, data, viewkwargs={}):
        request = self.getSessionRequest()
        v = self.get_view(kwargs=viewkwargs)
        if 'instance' in viewkwargs:
            f = v.get_form_class()(data=data, instance=viewkwargs['instance'])
            v.object = viewkwargs['instance']
        else:
            # get a instance of the model class for model based classes
            # - otherwise ignore
            try:
                f = self.get_form(data=data)
                v.object = v.model()
            except:
                pass #ignore - not a model based class
        v.request = request
        self.assertTrue(v.get_context_data(kwargs=viewkwargs))
        if isinstance(v, CreateView) or isinstance(v, UpdateView) or isinstance(v, LoginView):
            self.assertTrue(f.is_valid())
            self.assertTrue(v.form_valid(f))
        return request

class TemplateViewMixin(ViewMixin):

    def executeView(self, viewkwargs={}, postargs={}):
        request = self.getSessionRequest()
        v = self.get_view(kwargs=viewkwargs)

        mutable = request.POST._mutable
        request.POST._mutable = True
        request.POST.update(postargs)
        request.POST._mutable = mutable
        v.request = request

        c = v.get_context_data(**viewkwargs)
        if hasattr(v, 'post'):
            p = v.post(request, **viewkwargs)
        else:
            p = None

        return (c, p)
