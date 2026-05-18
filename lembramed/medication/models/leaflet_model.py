from django.db import models
from .medication_model import Medication
from .time_stamped_model import TimeStampedModel

class Leaflet(TimeStampedModel):
    medication_id = models.OneToOneField(
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