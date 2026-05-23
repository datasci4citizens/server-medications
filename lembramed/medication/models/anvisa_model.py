from datetime import date
from django.db import models
from .medication_model import Medication, Formato
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

class Presentation(TimeStampedModel):
    register_num = models.BigIntegerField(primary_key=True) # == regularion_num + "presentation_id"

    formato = models.OneToOneField(
        Formato,
        on_delete = models.CASCADE,
        related_name = 'presentsation'
    )
    dosage = models.CharField(max_length=100,default="")
    embalagem = models.CharField(max_length=100,default="") # lista de strings (primaria,secundaria...)
    administration = models.CharField(max_length=100,default="") # oral...
    conservation = models.TextField(default="") # Como armazenar soq mais seguro de ter!
    prescription_restriction = models.CharField(max_length=100,default="") # Sob Prescricao Medica...
    usage_restriction = models.CharField(max_length=50,default="") # grupo(adultos...)
    label = models.CharField(max_length=20,default="") # tarja
    can_be_fractioned = models.BooleanField(default=False) # pode partir/macerar o medicamento

    def __str__(self):
        return str(self.register_num)

class Register(TimeStampedModel):
    medication = models.OneToOneField(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'register',
    )
    regulation_num = models.IntegerField(primary_key=True,default=0000000000)
    expiration_date = models.DateField(default=date.today)
    presentation = models.ForeignKey(Presentation, on_delete=SET_NULL, blank=True, related_name='register')

    def __str__(self):
        return str(self.regulation_num)