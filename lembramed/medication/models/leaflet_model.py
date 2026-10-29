from datetime import date
from django.db import models
from .medication_model import Medication
from .presentation_model import Presentation
from .time_stamped_model import TimeStampedModel

class Leaflet(TimeStampedModel):
    medication = models.OneToOneField(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'leaflet',
        primary_key = True,
    )
    quando_nao_usar = models.TextField(default="")
    efeitos_colaterais = models.TextField(default="")
    indicacoes_para_uso = models.TextField(default="")
    esqueceu_medicamento = models.TextField(default="")
    como_usar_medicamento = models.TextField(default="")
    como_guardar_medicamento = models.TextField(default="")
    funcionamento_medicamento = models.TextField(default="") # oq seria isso?
    conhecimento_previo_necessario = models.TextField(default="")
    quantidade_a_mais = models.TextField(default="", blank=True, null=True)

    def __str__(self):
        return str(self.medication_id)
    