from django.db import models
from authentication.models import Person
import uuid, datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
import json
import os
from django.conf import settings

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

    def __str__(self):
       return f"{self.person_id} - {self.medication_id}"
    
    def get_priority_display(self):
        prio_dict = dict(self.PRIOTITY_TYPES)
        return prio_dict[priority]

    def check_interactions(person, new_medication):
        json_path = os.path.join(
            settings.BASE_DIR, 'api', 'src', 'lembramed_data', 'interactions.json'
        )

        try: # open json
            with open(json_path, 'r', encoding='utf-8') as f:
                all_interactions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Erro ao carregar interactions.json: {e}")

        new_ingredients = set(
            self.medication_id.ingredient
                .values_list('active_ingredient', flat=True)
        )

        # active ingridient of the new medication
        new_ingredients = {i.lower().strip() for i in new_ingredients}

        #active ingridient of the patient medications
        current_ingredients = set(
            Active_Ingredient.objects.filter(
                medication_id__takes__person_id=self.person_id
            )
            .exclude(medication_id=self.medication_id)
            .values_list('active_ingredient', flat=True)
            .distinct()
        )
        current_ingredients = {i.lower().strip() for i in current_ingredients}

        # check conflicts
        conflicts = []
        for interaction in all_interactions:
            ing1 = interaction.get('ingredient1', '').lower().strip()
            ing2 = interaction.get('ingredient2', '').lower().strip()

            # Verifica nos dois sentidos (A→B ou B→A)
            match = (
                (ing1 in new_ingredients and ing2 in current_ingredients) or
                (ing2 in new_ingredients and ing1 in current_ingredients)
            )

            if match:
                conflicts.append({
                    'ingredient1': interaction['ingredient1'],
                    'ingredient2': interaction['ingredient2'],
                    'severity': interaction.get('severity', 'Unknown'),
                    'description': interaction.get('description', ''),
                })

        return conflicts



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
            
    
    def __str__(self):
        horarios = ", ".join([t.strftime('%H:%M') for t in self.calculate_schedule()])
        return f"{self.taken_id} - Horários: {horarios}"