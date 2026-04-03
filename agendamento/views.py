from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .models import Agendamento


def gerar_horarios(data):
    horarios = []

    # horário de funcionamento
    if data.weekday() == 5:  # sábado
        inicio = datetime.combine(data, datetime.min.time()).replace(hour=9, minute=0)
        fim = datetime.combine(data, datetime.min.time()).replace(hour=14, minute=0)
    else:  # segunda a sexta
        inicio = datetime.combine(data, datetime.min.time()).replace(hour=9, minute=0)
        fim = datetime.combine(data, datetime.min.time()).replace(hour=17, minute=30)

    # gerar horários de 30 em 30 min
    atual = inicio
    while atual <= fim:
        horarios.append(atual.strftime("%H:%M"))
        atual += timedelta(minutes=30)

    # 🔥 buscar horários já ocupados no banco
    ocupados = Agendamento.objects.filter(data=data).values_list('horario', flat=True)

    # remover horários ocupados
    horarios_disponiveis = [h for h in horarios if h not in ocupados]

    return horarios_disponiveis


def home(request):
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

            # 🔥 SE VEIO HORÁRIO → SALVA NO BANCO
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

                # 🔥 REDIRECT (ESSA LINHA RESOLVE TUDO)
                return redirect("/")

            # 🔥 GERAR HORÁRIOS DISPONÍVEIS
            if data.weekday() != 6:  # bloqueia domingo
                horarios = gerar_horarios(data)

    return render(request, "agendamento.html", {
        "horarios": horarios,
        "dados": dados
    })