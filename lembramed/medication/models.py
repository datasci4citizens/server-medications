from django.db import models
from accounts.models import New_Person
import uuid, datetime
# Create your models here.

# django.core.exceptions.FieldError: Cannot resolve keyword 'medication_id' into field. Choices are: begin, classe_terapeutica, days, dosage, empresa, end, formato,
# id, name, person_id, person_id_id, principio_ativo, quantity, time

class Medication(models.Model):
    # medication_id = models.UUIDField(
    #     default = uuid.uuid4,
    #     editable = False,
    #     primary_key=True,
    #     db_column='medication_id'
    # )
    medication_id = models.IntegerField(
        primary_key = True,
        editable = False,
        db_column='medication_id',
        default=123
    )
    person_id = models.ForeignKey(
        'accounts.New_Person',
        on_delete=models.CASCADE,
        related_name='medications',
        db_column='person_id',
        null=True,
        blank=True,
    )
    DAYS_OF_WEEK = [
        ('mon', 'Segunda'),
        ('tue', 'Terça'),
        ('wed', 'Quarta'),
        ('thu', 'Quinta'),
        ('fri', 'Sexta'),
        ('sat', 'Sábado'),
        ('sun', 'Domingo'),
    ]
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, null=True)
    time = models.TimeField(null=True) # check how to put the format of time I wanna

    begin = models.DateField(default=datetime.date.today, null=True) # solve data problem
    end = models.DateField(default=datetime.date.today, null=True)

    days= models.CharField(max_length=50, null=True)
    formato= models.CharField(max_length=50, null=True)
    quantity = models.CharField(max_length= 50, null=True)
    empresa = models.CharField(max_length=100)
    principio_ativo = models.TextField()
    classe_terapeutica = models.CharField(max_length=100)
    
    # add the option to put more than one time of day
    # add option to put the day of the week

    def __str__(self):
        return str(self.medication_id)

    # @property
    # def medication_id(self):
    #     """Compatibility alias: return the model's primary key (`id`).

    #     The database already uses the default `id` column; some code
    #     expects `medication.medication_id`. Provide a read-only alias
    #     so queries don't require a separate `medication_id` column.
    #     """
    #     return self.id
    def get_days_display(self):
        day_dict = dict(self.DAYS_OF_WEEK)
        return ', '.join(day_dict[d] for d in self.days.split(',')) 

class Bula_data(models.Model):
    register_Num = models.IntegerField(
        # editable = False,
        primary_key = True,
    )
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
        return str(self.register_Num)