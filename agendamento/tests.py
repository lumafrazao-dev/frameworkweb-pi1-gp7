import json
from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse


class VoiceAppointmentTests(TestCase):
    @override_settings(GEMINI_API_KEY="test-key")
    @patch("agendamento.views._extract_appointment_data")
    def test_returns_only_missing_fields_after_voice_extraction(self, extract_data):
        extract_data.return_value = {
            "nome": "Maria Silva",
            "telefone": "13999990000",
            "placa": "",
            "data": (date.today() + timedelta(days=1)).isoformat(),
        }

        response = self.client.post(
            reverse("agendamento_por_voz"),
            data=json.dumps({"transcript": "Meu nome é Maria Silva", "dados": {}}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["campos_faltantes"], ["placa"])
        self.assertEqual(response.json()["dados"]["nome"], "Maria Silva")

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("agendamento.views._extract_appointment_data")
    def test_preserves_a_previously_collected_valid_field(self, extract_data):
        appointment_date = (date.today() + timedelta(days=1)).isoformat()
        extract_data.return_value = {
            "nome": "",
            "telefone": "13999990000",
            "placa": "ABC1D23",
            "data": appointment_date,
        }

        response = self.client.post(
            reverse("agendamento_por_voz"),
            data=json.dumps(
                {
                    "transcript": "Meu telefone é 13 99999 0000",
                    "dados": {"nome": "Maria Silva"},
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["campos_faltantes"], [])
        self.assertEqual(response.json()["dados"]["nome"], "Maria Silva")

    def test_rejects_a_request_without_a_transcript(self):
        response = self.client.post(
            reverse("agendamento_por_voz"),
            data=json.dumps({"transcript": "", "dados": {}}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
