from django.urls import path
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
    path('', escolher_opcao, name='escolher_opcao'), # <--- Agora a raiz é a página de escolha
    path('novo/', home, name='home'), # <--- O fluxo antigo de novo agendamento foi para /novo/
    path('buscar/', buscar_cadastro_para_editar, name='buscar_cadastro'), # <--- Nova rota de busca
    path('agendamento-por-voz/', processar_agendamento_por_voz, name='agendamento_por_voz'),
    path('editar/<int:pk>/', editar_agendamento, name='editar_agendamento'),
]
]
