from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .models import Agendamento #cod base

def gerar_horarios(data):
    horarios = [] #guarda os hrs
    if data.weekday() == 5:  #sab
        inicio = datetime.combine(data, datetime.min.time()).replace(hour=9, minute=0)
        fim = datetime.combine(data, datetime.min.time()).replace(hour=14, minute=0)
    else:  #swg a ses
        inicio = datetime.combine(data, datetime.min.time()).replace(hour=9, minute=0)
        fim = datetime.combine(data, datetime.min.time()).replace(hour=17, minute=30)

    atual = inicio #gera intervalo 30min
    while atual <= fim:
        horarios.append(atual.strftime("%H:%M"))
        atual += timedelta(minutes=30)

    #busca is hrs ocupados no banco
    ocupados = Agendamento.objects.filter(data=data).values_list('horario', flat=True)
    # exclui os hrs ocupados
    horarios_disponiveis = [h for h in horarios if h not in ocupados]
    return horarios_disponiveis

def home(request): #formulario
    horarios = []
    dados = {}
    if request.method == "POST":
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        placa = request.POST.get("placa")
        data_str = request.POST.get("data")
        horario = request.POST.get("horario")
        print("HORARIO RECEBIDO:", horario)
     
        dados = {
            "nome": nome,
            "telefone": telefone,
            "placa": placa,
            "data": data_str
        }
        if data_str:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
            #se preenchido salva no banco
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
                return redirect("/")
            #gera os hrs disponiveis
            if data.weekday() != 6:  #block os dom
                horarios = gerar_horarios(data)
                
    return render(request, "agendamento.html", {
        "horarios": horarios,
        "dados": dados
    })
