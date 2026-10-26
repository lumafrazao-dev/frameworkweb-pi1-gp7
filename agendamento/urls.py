"""from django.urls import path
from .views import home, processar_agendamento_por_voz

urlpatterns = [
    path('', home),
    path('agendamento-por-voz/', processar_agendamento_por_voz, name='agendamento_por_voz'),

from django.urls import path
from .views import (
    home, 
    processar_agendamento_por_voz, 
    editar_agendamento, 
    escolher_opcao, 
    buscar_cadastro_para_editar
)

urlpatterns = [
    path('', escolher_opcao, name='escolher_opcao'), # Raiz agora é a escolha inicial
    path('novo/', home, name='home'), # Fluxo antigo de agendamento virou /novo/
    path('buscar/', buscar_cadastro_para_editar, name='buscar_cadastro'), # Nova tela de busca por nome
    path('agendamento-por-voz/', processar_agendamento_por_voz, name='agendamento_por_voz'), # Voz continua funcionando
    path('editar/<int:pk>/', editar_agendamento, name='editar_agendamento'), # Tela para salvar alterações do ID específico
]
    
] """

from django.urls import path
from .views import (
    home, 
    processar_agendamento_por_voz, 
    editar_agendamento, 
    escolher_opcao, 
    buscar_cadastro_para_editar
)

urlpatterns = [
    path('', escolher_opcao, name='escolher_opcao'),
    path('novo/', home, name='home'),
    path('buscar/', buscar_cadastro_para_editar, name='buscar_cadastro'),
    path('agendamento-por-voz/', processar_agendamento_por_voz, name='agendamento_por_voz'),
    path('editar/<int:pk>/', editar_agendamento, name='editar_agendamento'),
]
