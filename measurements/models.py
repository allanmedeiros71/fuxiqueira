from django.db import models
from django.utils import timezone

from accounts.models import User


class Measurement(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medicoes")
    data_hora = models.DateTimeField(default=timezone.now)
    peso = models.DecimalField(max_digits=5, decimal_places=2, help_text="Peso em kg")
    imc = models.DecimalField(max_digits=4, decimal_places=2, help_text="Índice de Massa Corporal")
    percentual_gordura = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentual de gordura (%)")
    percentual_massa_muscular = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentual de massa muscular (%)")
    metabolismo_basal = models.IntegerField(help_text="Metabolismo basal em kcal")
    idade_metabolica = models.IntegerField(help_text="Idade metabólica em anos")
    indice_gordura_visceral = models.DecimalField(max_digits=4, decimal_places=1, help_text="Índice de gordura visceral")
    foto_frente = models.ImageField(upload_to="fotos/%Y/%m/", null=True, blank=True, help_text="Foto de frente")
    foto_perfil = models.ImageField(upload_to="fotos/%Y/%m/", null=True, blank=True, help_text="Foto de perfil")
    foto_costas = models.ImageField(upload_to="fotos/%Y/%m/", null=True, blank=True, help_text="Foto de costas")
    notas = models.TextField(null=True, blank=True, help_text="Notas adicionais sobre a medição")

    class Meta:
        verbose_name = "Medição de Bioimpedância"
        verbose_name_plural = "Medições de Bioimpedância"
        ordering = ["-data_hora"]

    def __str__(self):
        return f"{self.usuario.nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        if not self.imc and self.usuario.altura:
            self.imc = round(float(self.peso) / (float(self.usuario.altura) ** 2), 2)
        super().save(*args, **kwargs)
