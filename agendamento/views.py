import json
import logging
import re
from datetime import date, datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import Agendamento

logger = logging.getLogger(__name__)

VOICE_FIELDS = ("nome", "telefone", "placa", "data")
VOICE_FIELD_LABELS = {
    "nome": "nome completo",
    "telefone": "telefone",
    "placa": "placa do veículo",
    "data": "data preferida",
}

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


def _normalize_appointment_data(data):
    normalized = {field: "" for field in VOICE_FIELDS}

    name = str(data.get("nome", "")).strip()
    if re.fullmatch(r"[A-Za-zÀ-ÿ]+(?: [A-Za-zÀ-ÿ]+)+", name):
        normalized["nome"] = name

    phone_digits = re.sub(r"\D", "", str(data.get("telefone", "")))
    if phone_digits.startswith("55") and len(phone_digits) in (12, 13):
        phone_digits = phone_digits[2:]
    if len(phone_digits) in (10, 11):
        normalized["telefone"] = phone_digits

    plate = re.sub(r"[^A-Z0-9]", "", str(data.get("placa", "")).upper())
    if re.fullmatch(r"[A-Z]{3}[0-9][A-Z0-9][0-9]{2}", plate):
        normalized["placa"] = plate

    appointment_date = str(data.get("data", "")).strip()
    try:
        parsed_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
    except ValueError:
        parsed_date = None
    if parsed_date and parsed_date >= date.today() and parsed_date.weekday() != 6:
        normalized["data"] = parsed_date.isoformat()

    return normalized


def _extract_appointment_data(transcript, current_data):
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise RuntimeError("A integração com o Gemini não está configurada.")

    prompt = f"""
Extraia dados para um agendamento de funilaria no Brasil.
Data atual: {date.today().isoformat()}.
Transcrição do cliente: {transcript!r}.
Dados já coletados: {json.dumps(current_data, ensure_ascii=False)}.

Retorne somente um objeto JSON com as chaves nome, telefone, placa e data.
Mescle dados já coletados com novos dados. Use string vazia para qualquer dado
que não esteja claro. Converta a data para YYYY-MM-DD; não invente dados.
""".strip()
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "nome": {"type": "STRING"},
                    "telefone": {"type": "STRING"},
                    "placa": {"type": "STRING"},
                    "data": {"type": "STRING"},
                },
                "required": list(VOICE_FIELDS),
            },
        },
    }
    model = settings.GEMINI_MODEL
    query = urlencode({"key": api_key})
    request = Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?{query}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            result = json.load(response)
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)
    except (HTTPError, URLError, TimeoutError) as error:
        logger.warning("Gemini request failed: %s", error)
        raise RuntimeError("Não foi possível processar a fala agora.") from error
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        logger.warning("Gemini returned an invalid response: %s", error)
        raise RuntimeError("Não foi possível interpretar os dados informados.") from error


@require_POST
def processar_agendamento_por_voz(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "A solicitação de voz é inválida."}, status=400)

    transcript = payload.get("transcript", "")
    current_data = payload.get("dados", {})
    if not isinstance(transcript, str) or not transcript.strip():
        return JsonResponse({"error": "Não foi possível identificar a fala."}, status=400)
    if len(transcript) > 1000 or not isinstance(current_data, dict):
        return JsonResponse({"error": "A solicitação de voz é inválida."}, status=400)

    try:
        extracted_data = _extract_appointment_data(transcript.strip(), current_data)
    except RuntimeError as error:
        return JsonResponse({"error": str(error)}, status=503)

    data = _normalize_appointment_data(current_data)
    for field, value in _normalize_appointment_data(extracted_data).items():
        if value:
            data[field] = value
    missing_fields = [field for field in VOICE_FIELDS if not data[field]]
    return JsonResponse(
        {
            "dados": data,
            "campos_faltantes": missing_fields,
            "instrucao": (
                f"Diga apenas seu {VOICE_FIELD_LABELS[missing_fields[0]]}."
                if missing_fields
                else "Confira os dados antes de buscar os horários."
            ),
        }
    )


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
