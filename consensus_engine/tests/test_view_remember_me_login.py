from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from .mixins import OneUserMixin, ViewMixin

from consensus_engine.views import RememberMeLoginView
from consensus_engine.forms import RememberMeLoginForm

class RememberMeLoginViewTest(OneUserMixin, ViewMixin, TestCase):
    path = '/login'
    form = RememberMeLoginForm
    view = RememberMeLoginView

    def setUp(self):
        self.factory = RequestFactory()
        OneUserMixin.setUp(self)

    def test_remember_me(self):
        request = self.getValidView({'username': self.user.username,
                'password': 'top_secret',
                'remember_me': True})
        self.assertTrue(request.session.get_expiry_age() == 3000)
        self.assertFalse(request.session.get_expire_at_browser_close())


    def test_do_not_remember_me(self):
        request = self.getValidView({'username': self.user.username,
                'password': 'top_secret',
                'remember_me': False})
        self.assertTrue(request.session.get_expire_at_browser_close())
