from django.urls import path
from .views import home, processar_agendamento_por_voz

urlpatterns = [
    path('', home),
    path('agendamento-por-voz/', processar_agendamento_por_voz, name='agendamento_por_voz'),
]