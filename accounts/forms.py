from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nome = forms.CharField(max_length=100, required=True)
    data_nascimento = forms.DateField(required=True, widget=forms.DateInput(attrs={"type": "date"}))
    altura = forms.DecimalField(max_digits=4, decimal_places=2, required=True, help_text="Altura em metros (ex: 1.75)")

    class Meta:
        model = User
        fields = ("username", "email", "nome", "data_nascimento", "altura", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.nome = self.cleaned_data["nome"]
        user.data_nascimento = self.cleaned_data["data_nascimento"]
        user.altura = self.cleaned_data["altura"]
        # Usuário começa inativo, requer aprovação do administrador
        user.is_active = False
        if commit:
            user.save()
        return user
