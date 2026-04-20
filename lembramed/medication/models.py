from django.db import models
from authentication.models import Person
import uuid, datetime
from datetime import datetime, timedelta, combine, date
from django.utils import timezone
from django.core.exceptions import ValidationError

# Medication DATA from scrapers
class Medication(models.Model):
    # RegisterNum for ANVISA, RxCUI for RxNorm:
    medication_id = models.IntegerField(primary_key = True)

    # Information from Anvisa_Data:
    name = models.TextField()
    empresa = models.TextField()
    principio_ativo = models.TextField()
    classe_terapeutica = models.TextField()

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
    taken_id = models.AutoField(primary_key=True)

    # comprimido/dosagem, OK
    # forma de medicacao (pilula...), ok
    # horario, OK
    # quantidade, ok
    # lembrete de repor estoque (lembrete) ok
    # Int de prioridade da notificacao daquele medicamento
    # inicio e final de tratamento (opcional) OK

    PRIOTITY_TYPES = [
        (0, 'Low'),
        (1, 'Medium'),
        (2, 'High'),
        (3, 'Important')
    ]
    
    dosage = models.CharField(max_length=50, null=True)
    quantity = models.CharField(max_length= 50, null=True)
    priority = models.SmallIntegerField()
    formato= models.CharField(max_length=50, null=True) # type

    def __str__(self):
       return f"{self.person_id} - {self.medication_id}"
    

    def get_priority_display(self):
        prio_dict = dict(self.PRIOTITY_TYPES)
        return ', '.join(prio_dict[d] for d in self.days.split(',')) 


class TakeRecord(models.Model):

    taken_id = models.ForeignKey(    
        Take,
        on_delete = models.CASCADE,
        related_name = 'records',
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

    CYCLE_TYPE = [
        ('daily', 'Uma vez ao dia'),
        ('interval', 'De X em X horas'),

    ]

    cycle_type = models.CharField(max_length=10, choices=CYCLE_TYPE )
    begin = models.DateField(default=datetime.date.today) 
    end = models.DateField(default=datetime.date.today)
    days= models.CharField(max_length=50, null=True)
    take_at = models.TimeField(null=True, blank=True)  #first time you will take the medicine
    take_cicle = models.IntegerField(null=True, blank=True) # ex: take in 8-8 hours...
    state = models.CharField(max_length=50, null=True) # taken, forgortten, late...

    def get_days_display(self):
        day_dict = dict(self.DAYS_OF_WEEK)
        return ', '.join(day_dict[d] for d in self.days.split(',')) 

    def clean(self):
        if self.end < self.begin:
            raise ValidationError("Data final não pode ser menor que a inicial")

        if self.cycle_type == 'daily' and not self.take_at:
            raise ValidationError("Informe o horário em que o medicamento será tomado")

        if self.cycle_type == 'interval' and not self.take_cicle:
             raise ValidationError("Informe de quanto em quanto tempo o medicamento será tomado")
        
        if self.cycle_type == 'interval' and not self.take_at:
             raise ValidationError("Informe o horário em que o medicamento será tomado pela primeira vez")

    
    
    def calculate_schedule(self): # calculate when the patient is going to take the medication
        
        if not self.take_at:
            return []
        
        if self.cycle_type == 'daily' :
            return [self.take_at]
        
        if self.cycle_type == 'interval' and self.take_cicle:
            scheduels = []

            base_date = datetime.date.today()
            current_dt = datetime.datetime.combine(base_date, self.take_at)

            total_hours = 0
            while total_hours < 24:
                scheduels.append(current_dt.time())
                current_dt += datetime.timedelta(hours=self.take_cicle)
                tatal_hours += self.take_cicle

                if current_dt.date() > base_date:
                    break

            return scheduels
        return []
    

def define_state(self): # define the medication state based on when the medication was taken
    
    now = timezone.now()
    current_now = timezone.localtime(now)
    current_time = current_now.time()
    current_date = current_now.date()

    schedules = self.calculate_schedule()
    if not schedules:
        return None

    # Find the closest time of the scheduel to now
    past_schedules = [t for t in schedules if t <= current_time]
    
    if not past_schedules: 
        return "waiting"

    closest_scheduled_time = max(past_schedules) 

    scheduled_datetime = combine(current_date, closest_scheduled_time) # convert to datetime
    scheduled_datetime = timezone.make_aware(scheduled_datetime)

    # time diference
    time_gap = now - scheduled_datetime
     
    # future --> change the time limmit and atribute diferent time limits based on the medications priority 
    if time_gap > timedelta(minutes=30):
        self.state = "forgotten"
    
    if time_gap > timedelta(minutes=10) and  time_gap < timedelta(minutes=30):
        self.state = "late"
    else:
        self.state = "taken" 

    self.save() 
    return self.state

    
def calculate_stock(self): # determine the amount of pills left
        # future implementation --> other types of medications
        if not self.taken_id.formato or self.taken_id.formato.lower() != 'pílula':
            return None
        
        try:
            total_quantity = int(self.taken_id.quantity)
        except (ValueError, TypeError):
            return "Erro: Quantidade total de medicamentos não é um número válido."

        days_passed = (date.today() - self.begin).days

        days_passed = max(0, days_passed) # if is the first day

        if self.cycle_type == 'daily': 
            medications_taken = days_passed
            week_medication = 7
                
        elif self.cycle_type == 'interval' and self.take_cycle:
            medications_per_day = 24 // self.take_cycle
            medications_taken = days_passed * medications_per_day
            week_medication = 7*medications_per_day
        
        medication_left = total_quantity - medications_taken
        time_left = (self.end - date.today()).days


        if medication_left <= week_medication and time_left> 7: 
            # if the amount of pills left are less than the amount required in a week 
            # the amount of time left to take the medication is more than a week
            return f"Você tem {medication_left} pílulas restantes, reponha seu estoque."
          

def __str__(self):
        horarios = ", ".join([t.strftime('%H:%M') for t in self.calculate_schedule()])
        return f"{self.taken_id} - Horários: {horarios}"