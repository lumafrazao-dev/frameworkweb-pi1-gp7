from django import forms
from .models import Agendamento

# Formulário de busca 
class BuscaParametrosForm(forms.Form):
    termo_busca = forms.CharField(
        required=True,
        label="Digite seu nome completo",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: ABC-1234, 11999999999 ou João'})
    )

# Formulário para editar os dados cadastrais 
class EditarCadastroForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['nome']

# Formulário para remarcar (Data e Horário)
class RemarcarAgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['data', 'horario']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TextInput(attrs={'placeholder': 'HH:MM'}),
        }
