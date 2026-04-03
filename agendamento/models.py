from django.db import models

class Agendamento(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    placa = models.CharField(max_length=10)
    data = models.DateField()
    horario = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.nome} - {self.data} {self.horario}"