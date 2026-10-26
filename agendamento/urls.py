from django.urls import path
from .views import (
    home,
    editar_agendamento,
    escolher_opcao,
    buscar_cadastro_para_editar,
    api_guia_cadastro
)

urlpatterns = [
    path('', escolher_opcao, name='escolher_opcao'),
    path('novo/', home, name='home'),
    path('buscar/', buscar_cadastro_para_editar, name='buscar_cadastro'),
    path('api/guia-cadastro/', api_guia_cadastro, name='api_guia_cadastro'),
    path('editar/<int:pk>/', editar_agendamento, name='editar_agendamento'),
]
