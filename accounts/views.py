from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .forms import SignInForm


class SignInView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = SignInForm
    redirect_authenticated_user = True


class SignOutView(auth_views.LogoutView):
    pass


@login_required
def home(request):
    """Send each user to the right workspace for their role."""
    return redirect(request.user.home_url())
