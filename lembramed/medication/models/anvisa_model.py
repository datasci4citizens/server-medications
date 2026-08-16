from datetime import date
from django.db import models
from .medication_model import Medication, Presentation
from .time_stamped_model import TimeStampedModel

class Leaflet(TimeStampedModel):
    medication = models.OneToOneField(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'leaflet',
    )
    # Information from Leaflets:
    indicacoes_para_uso = models.TextField(default="")
    funcionamento_medicamento = models.TextField(default="")
    quando_nao_usar = models.TextField(default="")
    conhecimento_previo_necessario = models.TextField(default="")
    como_guardar_medicamento = models.TextField(default="")
    como_usar_medicamento = models.TextField(default="")
    esqueceu_medicamento = models.TextField(default="")
    efeitos_colaterais = models.TextField(default="")
    quantidade_a_mais = models.TextField(default="", blank=True, null=True) # erro, cuidado!

    def __str__(self):
        return str(self.medication_id)

class Register(TimeStampedModel):
    medication = models.OneToOneField(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'register',
    )
    regulation_num = models.IntegerField(primary_key=True,default=0000000000)
    expiration_date = models.DateField(default=date.today)
    presentation = models.ForeignKey(Presentation, on_delete=models.SET_NULL, blank=True, related_name='register', null=True)

    def __str__(self):
        return str(self.regulation_num)