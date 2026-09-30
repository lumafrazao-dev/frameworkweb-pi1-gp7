# frameworkweb-pi1-gp7

## Agendamento por voz

O recurso usa o reconhecimento de fala do navegador e o Gemini para identificar
nome completo, telefone, placa e data preferida. Configure a chave somente no
ambiente de execução, nunca no repositório:

```powershell
$env:GEMINI_API_KEY = "sua-chave"
python manage.py runserver
```

Em produção, cadastre `GEMINI_API_KEY` nas variáveis de ambiente. Opcionalmente,
`GEMINI_MODEL` seleciona o modelo; o padrão é `gemini-2.5-flash`.