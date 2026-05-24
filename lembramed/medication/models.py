from django.db import models
from authentication.models import Person
import uuid
import datetime
from datetime import datetime, timedelta, date 
from django.utils import timezone
from django.core.exceptions import ValidationError
import json
import os
from django.conf import settings

class Medication(models.Model):
    # RegisterNum for ANVISA, RxCUI for RxNorm:
    medication_id = models.IntegerField(primary_key = True)

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
        related_name = 'therapeutic_class',
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

# class med_format(models.Model):
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

    # comprimido/dosagem, OK
    # forma de medicacao (pilula...), ok
    # horario, OK
    # quantidade, ok
    # lembrete de repor estoque (lembrete) ok
    # Int de prioridade da notificacao daquele medicamento
    # inicio e final de tratamento (opcional) OK

    quantity = models.CharField(max_length= 50, null=True) # estoque
    med_format = models.CharField(max_length=50, null=True) # type

    def __str__(self):
       return f"{self.person_id} - {self.medication_id}"
    

    def check_interactions(self):
        from django.conf import settings

        json_path = os.path.join(
            settings.BASE_DIR, 'api', 'src', 'lembramed_data', 'Interactions.json'
        )

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                all_interactions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Erro ao carregar interactions.json: {e}")

        # O arquivo real do projeto pode vir como uma tabela com
        # {'columns': [...], 'data': [...]}. Nesse caso, ele não contém
        # pares ingredient1/ingredient2 e não deve quebrar o salvamento.
        if isinstance(all_interactions, dict):
            all_interactions = all_interactions.get('data', [])
        if not isinstance(all_interactions, list):
            return []

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
            if not isinstance(interaction, dict):
                continue

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
            

        major_conflicts = [c for c in conflicts if c['severity'] == 'Major']
        if major_conflicts:
            descriptions = '; '.join(
                f"{c['ingredient1']} × {c['ingredient2']}: {c['description']}"
                for c in major_conflicts
            )
            raise ValidationError(
                f"Esses medicamentos não devem ser consumidos simultaneamente. "
                f"Consulte um médico. Interações graves encontradas: {descriptions}"
            )

        return conflicts

    def save(self, *args, **kwargs):
        if not self.pk:
            self.check_interactions()
        
        super().save(*args,**kwargs)

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

    cycle_type = models.CharField(max_length=10, choices=CYCLE_TYPE, default='daily')
    begin = models.DateField(default=datetime.today) 
    end = models.DateField(default=datetime.today)
    days= models.CharField(max_length=50, null=True)
    take_at = models.TimeField(null=True, blank=True)  #first time you will take the medicine
    take_cycle = models.IntegerField(null=True, blank=True) # ex: take in 8-8 hours...
    state = models.CharField(max_length=50, null=True) # taken, forgortten

    def get_days_display(self):
        day_dict = dict(self.DAYS_OF_WEEK)
        return ', '.join(day_dict[d] for d in self.days.split(',')) 

    def clean(self):
        if self.end < self.begin:
            raise ValidationError("Data final não pode ser menor que a inicial")

        if self.cycle_type == 'daily' and not self.take_at:
            raise ValidationError("Informe o horário em que o medicamento será tomado")

        if self.cycle_type == 'interval' and not self.take_cycle:
             raise ValidationError("Informe de quanto em quanto tempo o medicamento será tomado")
        
        if self.cycle_type == 'interval' and not self.take_at:
             raise ValidationError("Informe o horário em que o medicamento será tomado pela primeira vez")

    
    
    def calculate_schedule(self): # calculate when the patient is going to take the medication
        
        if not self.take_at:
            return []
        
        if self.cycle_type == 'daily' :
            return [self.take_at]
        
        if self.cycle_type == 'interval' and self.take_cycle:
            scheduels = []

            base_date = date.today()
            current_dt = datetime.combine(base_date, self.take_at)

            total_hours = 0
            while total_hours < 24:
                scheduels.append(current_dt.time())
                current_dt += timedelta(hours=self.take_cycle)
                total_hours += self.take_cycle

                if current_dt.date() > base_date:
                    break

            return scheduels
        return []
    

    def define_state(self): # define the medication state based on when the medication was taken
    
        now = timezone.now() # review the when_was_taken 
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

        scheduled_datetime = datetime.combine(current_date, closest_scheduled_time) # convert to datetime
        scheduled_datetime = timezone.make_aware(scheduled_datetime)

        # time diference
        time_gap = now - scheduled_datetime
        
        # change: removed the latte state
        if time_gap > timedelta(minutes=10):
            self.state = "forgotten"
        else:
            self.state = "taken"

        self.save() 
        return self.state

        
    def calculate_stock(self): # determine the amount of pills left
            # future implementation --> other types of medications
            if not self.taken_id.med_format or self.taken_id.med_format.lower() != 'pílula':
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
            med_schedules = ", ".join([t.strftime('%H:%M') for t in self.calculate_schedule()])
            return f"{self.taken_id} - Horários: {med_schedules}"
