from django.db import models
from authentication.models import Person
import uuid, datetime

# Medication DATA from scrapers
class Medication(models.Model):
    # RegisterNum for ANVISA, RxCUI for RxNorm:
    medication_id = models.IntegerField(primary_key = True)

    # Information from Anvisa_Data:
    name = models.CharField(max_length=100)
    empresa = models.CharField(max_length=100)
    principio_ativo = models.TextField()
    classe_terapeutica = models.CharField(max_length=100)

    # Information from Leaflets:
    indicacoes_para_uso = models.TextField()
    funcionamento_medicamento = models.TextField()
    quando_nao_usar = models.TextField()
    conhecimento_previo_necessario = models.TextField()
    como_guardar_medicamento = models.TextField()
    como_usar_medicamento = models.TextField()
    esqueceu_medicamento = models.TextField()
    efeitos_colaterais = models.TextField()
    quantidade_a_mais = models.TextField()

    def __str__(self):
        return str(self.medication_id)

# One Person (New_Person)X takes (Medication)Y 
class Take(models.Model):
    person_id = models.ForeignKey(
        'authentication.Person',
        on_delete = models.CASCADE,
        related_name = 'takes'
    )
    medication_id = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'takes',
    )
   
    # comprimido/dosagem, OK
    # forma de medicacao (pilula...), ok
    # horario, OK
    # quantidade, ok
    # lembrete de repor estoque (lembrete), !!!!!!!!!
    # Int de prioridade da notificacao daquele medicamento
    # inicio e final de tratamento (opcional) OK

    
    DAYS_OF_WEEK = [
        ('mon', 'Segunda'),
        ('tue', 'Terça'),
        ('wed', 'Quarta'),
        ('thu', 'Quinta'),
        ('fri', 'Sexta'),
        ('sat', 'Sábado'),
        ('sun', 'Domingo'),
    ]
    PRIOTITY_TYPES = [
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Important')
    ]
    
    dosage = models.CharField(max_length=50, null=True)
    time = models.TimeField(null=True) 
    begin = models.DateField(default=datetime.date.today, null=True) 
    end = models.DateField(default=datetime.date.today, null=True)
    # add the option to put more than one time of day
    # add option to put the day of the week
    days= models.CharField(max_length=50, null=True)
    quantity = models.CharField(max_length= 50, null=True)
    priority = models.SmallIntegerField()
    state = models.CharField(max_length=50, null=True) # taken, forgortten, late...
    formato= models.CharField(max_length=50, null=True) # type

    def get_days_display(self):
        day_dict = dict(self.DAYS_OF_WEEK)
        return ', '.join(day_dict[d] for d in self.days.split(',')) 

    def get_priority_display(self):
        prio_dict = dict(self.DAYS_OF_WEEK)
        return ', '.join(prio_dict[d] for d in self.days.split(',')) 