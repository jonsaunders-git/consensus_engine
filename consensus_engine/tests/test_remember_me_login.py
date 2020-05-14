from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import OneUserMixin

from consensus_engine.views import RememberMeLoginView
from consensus_engine.forms import RememberMeLoginForm

class RememberMeLoginViewTest(OneUserMixin, TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        OneUserMixin.setUp(self)

    def getSessionRequest(self, path='/login'):
        request = self.factory.get(path)
        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        request.user = self.user

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        return request

    def getValidView(self, remember_me):
        request = self.getSessionRequest()
        data = {'username': self.user.username,
                'password': 'top_secret',
                'remember_me': remember_me}
        f = RememberMeLoginForm(data=data)
        v = RememberMeLoginView()
        v.request = request
        self.assertTrue(f.is_valid())
        self.assertTrue(v.form_valid(f))
        return request


    def test_remember_me(self):
        request = self.getValidView(remember_me=True)
        self.assertTrue(request.session.get_expiry_age() == 3000)
        self.assertFalse(request.session.get_expire_at_browser_close())


    def test_do_not_remember_me(self):
        request = self.getValidView(remember_me=False)
        self.assertTrue(request.session.get_expire_at_browser_close())
