from django.shortcuts import render
from django.views.generic import CreateView, DetailView, ListView
from django.forms import Form
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from .forms import RegisterUserForm
from products.models.models import Cards
from users.mixins import UserLoginRequiredMixin
from .filters import *


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = "users/register.html"
    success_url = reverse_lazy("home")


class LoginUserView(LoginView):
    form_class = AuthenticationForm
    template_name = "users/login.html"

    def get_success_url(self):
        return reverse_lazy("home")


class BaseAccountView(UserLoginRequiredMixin):
    def get_context_data(self, **kwargs):
        current_context = super().get_context_data(**kwargs)
        current_context.update({"current_section": self._get_curren_section()})

        if "pk" in self.kwargs and int(self.kwargs.get("pk")) == self.request.user.id:
            current_context.update({"is_self_account": True})

        return current_context

    def get_user(self, url_pk_name: str = "pk"):
        if not self.kwargs.get(url_pk_name):
            raise KeyError(f"Not found url-arg: '{url_pk_name=}'")

        return User.objects.filter(id=self.kwargs.get(url_pk_name))

    def _get_curren_section(self):
        try:
            return self._section
        except AttributeError:
            return


class AccountInfoView(BaseAccountView, DetailView):
    model = User
    template_name = "users/account-info.html"
    context_object_name = "user"

    _section = "info"

    def get_queryset(self):
        return super().get_user()


class AccountCardsView(BaseAccountView, ListView):
    model = Cards
    template_name = "users/account-cards.html"
    context_object_name = "items"

    _section = "cards"

    def get_queryset(self):
        user = super().get_user()[0]
        return self.model.objects.filter(author=user)


class LogoutUserView(LogoutView):
    next_page = reverse_lazy("home")
