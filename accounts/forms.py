from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nome = forms.CharField(max_length=100, required=True)
    data_nascimento = forms.DateField(required=True, widget=forms.DateInput(attrs={"type": "date"}))
    altura = forms.DecimalField(max_digits=4, decimal_places=2, required=True, help_text="Altura em metros (ex: 1.75)")
    meta_peso = forms.DecimalField(max_digits=5, decimal_places=2, required=False, help_text="Meta de peso em kg (opcional)")
    meta_gordura = forms.DecimalField(max_digits=5, decimal_places=2, required=False, help_text="Meta de percentual de gordura (opcional)")

    class Meta:
        model = User
        fields = ("username", "email", "nome", "data_nascimento", "altura", "meta_peso", "meta_gordura", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.nome = self.cleaned_data["nome"]
        user.data_nascimento = self.cleaned_data["data_nascimento"]
        user.altura = self.cleaned_data["altura"]
        user.meta_peso = self.cleaned_data.get("meta_peso")
        user.meta_gordura = self.cleaned_data.get("meta_gordura")
        # Usuário começa inativo, requer aprovação do administrador
        user.is_active = False
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("nome", "data_nascimento", "altura", "meta_peso", "meta_gordura")
        widgets = {
            "nome": forms.TextInput(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "data_nascimento": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date", "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "altura": forms.NumberInput(attrs={"step": "0.01", "placeholder": "1.75", "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "meta_peso": forms.NumberInput(attrs={"step": "0.1", "placeholder": "70.0", "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "meta_gordura": forms.NumberInput(attrs={"step": "0.1", "placeholder": "15.0", "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
        }
