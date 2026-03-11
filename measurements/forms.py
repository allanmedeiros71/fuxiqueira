from django import forms
from django.utils import timezone

from .models import Measurement


class MeasurementForm(forms.ModelForm):
    data_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                "type": "datetime-local",
            }
        ),
        initial=timezone.now,
    )

    class Meta:
        model = Measurement
        fields = [
            "data_hora",
            "peso",
            "imc",
            "percentual_gordura",
            "percentual_massa_muscular",
            "metabolismo_basal",
            "idade_metabolica",
            "indice_gordura_visceral",
            "foto_frente",
            "foto_perfil",
            "foto_costas",
            "notas",
        ]
        widgets = {
            "peso": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Ex: 70.5",
                    "step": "0.1",
                    "min": "0",
                }
            ),
            "imc": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Ex: 22.5",
                    "step": "0.1",
                    "min": "0",
                }
            ),
            "percentual_gordura": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Ex: 15.5",
                    "step": "0.1",
                    "min": "0",
                    "max": "100",
                }
            ),
            "percentual_massa_muscular": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Ex: 45.2",
                    "step": "0.1",
                    "min": "0",
                    "max": "100",
                }
            ),
            "metabolismo_basal": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Ex: 1650",
                    "min": "0",
                }
            ),
            "idade_metabolica": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Ex: 25",
                    "min": "0",
                }
            ),
            "indice_gordura_visceral": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Ex: 5.5",
                    "step": "0.1",
                    "min": "0",
                }
            ),
            "foto_frente": forms.FileInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "accept": "image/*",
                    "capture": "camera",
                }
            ),
            "foto_perfil": forms.FileInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "accept": "image/*",
                    "capture": "camera",
                }
            ),
            "foto_costas": forms.FileInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "accept": "image/*",
                    "capture": "camera",
                }
            ),
            "notas": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Notas adicionais sobre esta medição (opcional)",
                    "rows": 3,
                }
            ),
        }
