from django.contrib import admin
from .models import Measurement


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'data_hora', 'peso', 'imc', 'percentual_gordura', 'percentual_massa_muscular')
    list_filter = ('usuario', 'data_hora')
    search_fields = ('usuario__nome', 'usuario__email')
    ordering = ('-data_hora',)
    readonly_fields = ('data_hora',)
    
    fieldsets = (
        ('Informações do Usuário', {
            'fields': ('usuario', 'data_hora')
        }),
        ('Medições da Balança', {
            'fields': ('peso', 'imc', 'percentual_gordura', 'percentual_massa_muscular')
        }),
        ('Metabolismo', {
            'fields': ('metabolismo_basal', 'idade_metabolica', 'indice_gordura_visceral')
        }),
    )
