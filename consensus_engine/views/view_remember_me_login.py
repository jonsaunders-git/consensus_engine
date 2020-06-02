from django.contrib.auth.views import LoginView
from consensus_engine.forms import RememberMeLoginForm


class RememberMeLoginView(LoginView):
    form_class = RememberMeLoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data['remember_me']
        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(3000)
        self.request.session.modified = True
        return super().form_valid(form)
