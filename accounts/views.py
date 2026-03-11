from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm


class CustomLoginView(LoginView):
    template_name = "accounts/login_standalone.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("dashboard")


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/signup_standalone.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Solicitação de cadastro enviada com sucesso! Aguarde aprovação do administrador para acessar o sistema.")
        return response
