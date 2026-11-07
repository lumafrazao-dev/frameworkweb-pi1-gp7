from django.contrib import admin
from .models import Agendamento

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'placa', 'data', 'horario')
    search_fields = ('nome')

# Register your models here.
