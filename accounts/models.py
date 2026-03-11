from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField()
    altura = models.DecimalField(max_digits=4, decimal_places=2, help_text="Altura em metros (ex: 1.75)")
    meta_peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Meta de peso em kg (opcional)")
    meta_gordura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Meta de percentual de gordura (opcional)")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "nome", "data_nascimento", "altura"]

    def __str__(self):
        return self.nome

    @property
    def idade(self):
        return int((timezone.now().date() - self.data_nascimento).days / 365.25)
