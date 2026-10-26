import json
import logging
from datetime import date, datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from .models import Agendamento

logger = logging.getLogger(__name__)


def gerar_horarios(data):
    horarios = []
    if data.weekday() == 5:  # Sábado
        inicio = datetime.combine(data, datetime.min.time()).replace(hour=9, minute=0)
        fim = datetime.combine(data, datetime.min.time()).replace(hour=14, minute=0)
    else:  # Segunda a sexta
        inicio = datetime.combine(data, datetime.min.time()).replace(hour=9, minute=0)
        fim = datetime.combine(data, datetime.min.time()).replace(hour=17, minute=30)

    atual = inicio
    while atual <= fim:
        horarios.append(atual.strftime("%H:%M"))
        atual += timedelta(minutes=30)

    ocupados = Agendamento.objects.filter(data=data).values_list('horario', flat=True)
    horarios_disponiveis = [h for h in horarios if h not in ocupados]
    return horarios_disponiveis


@require_GET
def api_guia_cadastro(request):
    """API de acessibilidade para auxiliar pessoas com baixa leitura no preenchimento."""
    campo = request.GET.get("campo", "").strip().lower()
    
    guias = {
        "nome": {
            "titulo": "Qual é o seu nome?",
            "explicacao": "Escreva seu nome completo igual está no seu documento.",
            "exemplo": "Exemplo: Maria da Silva Santos",
        },
        "telefone": {
            "titulo": "Qual o número do seu WhatsApp ou celular?",
            "explicacao": "Digite o número com o DDD da sua cidade para a oficina te mandar a confirmação.",
            "exemplo": "Exemplo: 13 99999-0000",
        },
        "placa": {
            "titulo": "Qual é a placa do seu veículo?",
            "explicacao": "São aquelas letras e números que ficam no parachoque da frente ou atrás do veículo.",
            "exemplo": "Exemplo: ABC 1234",
        },
        "data": {
            "titulo": "Para qual dia você quer marcar?",
            "explicacao": "Escolha o dia que você quer levar o veículo na oficina.",
            "exemplo": "Exemplo: Selecione no calendário.",
        }
    }
    
    if campo in guias:
        return JsonResponse({
            "status": "sucesso",
            "dados_campo": guias[campo]
        }, json_dumps_params={'ensure_ascii': False})
    
    return JsonResponse({
        "status": "sucesso",
        "mensagem_geral": "Bem-vindo! Vamos preencher o cadastro juntos, passo a passo."
    }, json_dumps_params={'ensure_ascii': False})


def home(request):
    horarios = []
    dados = {}
    agendamento_confirmado = False
    
    if request.method == "POST":
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        placa = request.POST.get("placa")
        data_str = request.POST.get("data")
        horario = request.POST.get("horario")
     
        dados = {
            "nome": nome,
            "telefone": telefone,
            "placa": placa,
            "data": data_str
        }
        if data_str:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
            if horario:
                existe = Agendamento.objects.filter(data=data, horario=horario).exists()
                if not existe:
                    Agendamento.objects.create(
                        nome=nome,
                        telefone=telefone,
                        placa=placa,
                        data=data,
                        horario=horario
                    )
                    agendamento_confirmado = True
                return render(request, "agendamento.html", {
                    "horarios": horarios,
                    "dados": dados,
                    "agendamento_confirmado": agendamento_confirmado
                })
            
            if data.weekday() != 6:
                horarios = gerar_horarios(data)
                
    return render(request, "agendamento.html", {
        "horarios": horarios,
        "dados": dados,
        "agendamento_confirmado": agendamento_confirmado
    })


def escolher_opcao(request):
    return render(request, "escolher_opcao.html")


def buscar_cadastro_para_editar(request):
    erro = False
    if request.method == "POST":
        nome_busca = request.POST.get("nome_busca", "").strip()
        agendamento = Agendamento.objects.filter(nome__icontains=nome_busca).order_by('-data').first()
        
        if agendamento:
            return redirect('editar_agendamento', pk=agendamento.pk)
        else:
            erro = True

    return render(request, "buscar_cadastro.html", {"erro": erro})


def editar_agendamento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    horarios = []
    
    if agendamento.data.weekday() != 6:
        horarios = gerar_horarios(agendamento.data)

    dados = {
        "nome": agendamento.nome,
        "telefone": agendamento.telefone,
        "placa": agendamento.placa,
        "data": agendamento.data.strftime("%Y-%m-%d"),
        "horario": agendamento.horario
    }

    if request.method == "POST":
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        placa = request.POST.get("placa")
        data_str = request.POST.get("data")
        horario = request.POST.get("horario")

        dados = {
            "nome": nome,
            "telefone": telefone,
            "placa": placa,
            "data": data_str,
            "horario": horario
        }

        if data_str:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
            
            if horario:
                existe = Agendamento.objects.filter(data=data, horario=horario).exclude(pk=pk).exists()
                if not existe:
                    agendamento.nome = nome
                    agendamento.telefone = telefone
                    agendamento.placa = placa
                    agendamento.data = data
                    agendamento.horario = horario
                    agendamento.save()
                    return redirect("escolher_opcao")
            
            if data.weekday() != 6:
                horarios = gerar_horarios(data)

    return render(request, "agendamento.html", {
        "horarios": horarios,
        "dados": dados,
        "agendamento": agendamento,
        "editando": True
    })
