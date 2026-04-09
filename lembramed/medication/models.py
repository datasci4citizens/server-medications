from django.db import models
from authentication.models import Person
import uuid, datetime, json, os
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, date, timedelta

class Medication(models.Model):
    # RegisterNum for ANVISA, RxCUI for RxNorm:
    medication_id = models.IntegerField(primary_key = True)

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

class Medication_Name(models.Model):
    medication_id = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'name',
    )
    name = models.TextField()

    def __str__(self):
        return self.name

class Active_Ingredient(models.Model):
    medication_id = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'ingredient',
    )
    active_ingredient = models.TextField()

    def __str__(self):
        return self.active_ingredient

class ingredient_Interaction(models.Model):
    active_ingredient1 = models.ForeignKey(
        Active_Ingredient,
        on_delete = models.CASCADE,
        related_name = 'ingredient1'
    )
    active_ingredient2 = models.ForeignKey(
        Active_Ingredient,
        on_delete = models.CASCADE,
        related_name = 'ingredient2'
    )
    # Major, Moderate, Minor, Unknown
    severity = models.CharField(max_length=10)
    description = models.TextField()

    def __str__(self):
        return self.severity

class Therapeutic_Class(models.Model):
    medication_id = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'class',
    )
    therapeutic_class = models.TextField()

    def __str__(self):
        return self.therapeutic_class

class Brand(models.Model):
    medication_id = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'brand',
    )
    brand = models.TextField()

    def __str__(self):
        return self.brand
    
class Dosage(models.Model):
    medication_id = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'dosage',
    )
    dosage = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.dosage

class Company(models.Model):
    medication_id = models.ForeignKey(
        Medication,
        on_delete = models.CASCADE,
        related_name = 'company',
    )
    company = models.TextField()

    def __str__(self):
        return self.company

# class Formato(models.Model):
#     medication_id = models.ForeignKey(
#         Medication,
#         on_delete = models.CASCADE,
#         related_name = 'formato',
#     )
#     formato = models.CharField(max_length=50, null=True) # type

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

    PRIOTITY_TYPES = [
        (0, 'Low'),
        (1, 'Medium'),
        (2, 'High'),
        (3, 'Important')
    ]
    
    priority = models.SmallIntegerField()
    quantity = models.CharField(max_length= 50, null=True) # estoque

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

    def __str__(self):
       return f"{self.person_id} - {self.medication_id}"
    
    def get_priority_display(self):
        prio_dict = dict(self.PRIOTITY_TYPES)
        return prio_dict[priority]

    def check_interactions(self):
        from django.conf import settings

        json_path = os.path.join(
            settings.BASE_DIR, 'api', 'src', 'lembramed_data', 'interactions.json'
        )

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                all_interactions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Erro ao carregar interactions.json: {e}")

        new_ingredients = {
            i.lower().strip()
            for i in self.medication_id.ingredient.values_list('active_ingredient', flat=True)
        }

        current_ingredients = {
            i.lower().strip()
            for i in Active_Ingredient.objects.filter(
                medication_id__takes__person_id=self.person_id
            ).exclude(
                medication_id=self.medication_id
            ).values_list('active_ingredient', flat=True).distinct()
        }

        conflicts = []
        for interaction in all_interactions:
            ing1 = interaction.get('ingredient1', '').lower().strip()
            ing2 = interaction.get('ingredient2', '').lower().strip()

            match = (
                (ing1 in new_ingredients and ing2 in current_ingredients) or
                (ing2 in new_ingredients and ing1 in current_ingredients)
            )

            if match:
                conflicts.append({
                    'ingredient1': interaction['ingredient1'],
                    'ingredient2': interaction['ingredient2'],
                    'severity':    interaction.get('severity', 'Unknown'),
                    'description': interaction.get('description', ''),
                })

        return conflicts
    
    def clean(self):
        if self.end <self.begin:
            raise ValidationError("Data final não pode ser menor que a inicial")

        if self.cycle_type == 'daily' and not self.take_at:
            raise ValidationError("Informe o horário em que o medicamento será tomado")

        if self.cycle_type == 'interval' and not self.take_cicle:
             raise ValidationError("Informe de quanto em quanto tempo o medicamento será tomado")
        
        if self.cycle_type == 'interval' and not self.take_at:
             raise ValidationError("Informe o horário em que o medicamento será tomado pela primeira vez")
    
    def calculate_schedule(self):
        
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
                total_hours += self.take_cicle

                if current_dt.date() > base_date:
                    break

            return scheduels
        return []

    def get_days_display(self):
        day_dict = dict(self.DAYS_OF_WEEK)
        return ', '.join(day_dict[d] for d in self.days.split(',')) 
            
    def __str__(self):
        horarios = ", ".join([t.strftime('%H:%M') for t in self.calculate_schedule()])
        return f"{self.taken_id} - Horários: {horarios}"
    


class TakeRecord(models.Model):
    taken_id = models.ForeignKey(    
        Take,
        on_delete = models.CASCADE,
        related_name = 'records',
    )

    when_was_taked = models.TimeField(null=True, blank=True) 

    STATE_CHOICES = [
        ('taken', 'Tomado'),
        ('late', 'Atrasado'),
        ('skipped', 'Esquecido'),
        ('advance', 'Adiantado')
    ]
    state = models.CharField(max_length=50, choices=STATE_CHOICES, null=True)
    
    PRIORITY_TOLERANCE_MAP = {
        0: 60,
        1: 30,
        2: 10,
        3: 5
    }

    
    def mark_medication_as_taken(take_instance, time_now): # para multiplos horarios de um remedio
        # 1. Pega todos os horários previstos 
        schedules = take_instance.calculate_schedule()
        
        # 2. Encontra o horário mais próximo do agora
        closest_schedule = min(schedules, key=lambda x: abs(
            datetime.combine(date.today(), x) - datetime.combine(date.today(), time_now)
        ))

    
        record = TakeRecord.objects.create(
            taken_id=take_instance,
            when_was_taked=time_now
        )
        record.determine_state(closest_schedule)
    
    def determine_state(self, scheduled_time):

        if not self.when_was_taked:
            self.state = 'skipped'
            return
        today = date.today()
        dt_scheduled = datetime.combine(today, scheduled_time)
        dt_taken = datetime.combine(today, self.when_was_taked)

        diff_minutes = (dt_taken - dt_scheduled).total_seconds() /60
        
        tolerance = self.PRIORITY_TOLERANCE_MAP.get(self.taken_id.priority, 5)

        if diff_minutes < -tolerance:
            self.state = 'advance'
        elif abs(diff_minutes) <= tolerance:
            self.state = 'taken'
        elif diff_minutes > tolerance:
    
            if diff_minutes > 120:
                self.state = 'skipped'
            else:
                self.state = 'late'
        
        self.save()
    def __str__(self):
       return f"{self.taken_id} - {self.when_was_taked}"