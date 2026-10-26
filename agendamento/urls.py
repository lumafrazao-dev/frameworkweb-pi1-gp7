from django.urls import path
from .views import home, processar_agendamento_por_voz

urlpatterns = [
    path('', home),
    path('agendamento-por-voz/', processar_agendamento_por_voz, name='agendamento_por_voz'),

    # No urls.py
urlpatterns = [
    path('', escolher_opcao, name='escolher_opcao'),
    path('novo/', home, name='home'),
    path('buscar/', buscar_cadastro_para_editar, name='buscar_cadastro'),
    path('agendamento-por-voz/', processar_agendamento_por_voz, name='agendamento_por_voz'),
    path('editar/<int:pk>/', editar_agendamento, name='editar_agendamento'),
]
]
