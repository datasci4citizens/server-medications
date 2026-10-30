from django.db import models
from authentication.models import Person
import os,json
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from ..models import Medication, Active_Ingredient
from .time_stamped_model import TimeStampedModel
from datetime import datetime, timedelta, date, time

class Take(TimeStampedModel):
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
    client_id = models.CharField(max_length=100, blank=True, default='')
    dosage = models.CharField(max_length=100, blank=True, default='')
    brand = models.CharField(max_length=255, blank=True, default='')
    type = models.CharField(max_length=20, default='tablet')
    stock_reminder_enabled = models.BooleanField(default=False)
    stock_reminder_threshold = models.PositiveIntegerField(default=5)
    dose_status = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['person_id', 'client_id'],
            condition=~models.Q(client_id=''), name='unique_patient_client_take',
        )]

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
    
    priority = models.SmallIntegerField()
    quantity = models.CharField(max_length= 50, null=True) # estoque

    def __str__(self):
       return f"{self.person_id} - {self.medication_id}"
    
    def get_priority_display(self, priority):
        prio_dict = dict(self.PRIOTITY_TYPES)
        return prio_dict[priority]

    def check_interactions(self, person, new_medication):
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

class TakeRecord(TimeStampedModel):
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
    begin = models.DateField(default=datetime.today) 
    end = models.DateField(null=True, blank=True)
    days= models.CharField(max_length=50, null=True)
    take_at = models.TimeField(null=True, blank=True)  #first time you will take the medicine
    take_cycle = models.IntegerField(null=True, blank=True) # ex: take in 8-8 hours...
    state = models.CharField(max_length=50, null=True) # taken, forgortten, late...

    def get_days_display(self):
        day_dict = dict(self.DAYS_OF_WEEK)
        return ', '.join(day_dict[d] for d in self.days.split(',')) 

    def clean(self):
        if self.end and self.end < self.begin:
            raise ValidationError("Data final não pode ser menor que a inicial")

        if self.cycle_type == 'daily' and not self.take_at:
            raise ValidationError("Informe o horário em que o medicamento será tomado")

        if self.cycle_type == 'interval' and not self.take_cycle:
             raise ValidationError("Informe de quanto em quanto tempo o medicamento será tomado")
        
        if self.cycle_type == 'interval' and not self.take_at:
             raise ValidationError("Informe o horário em que o medicamento será tomado pela primeira vez")

    
  
    def calculate_schedule(self, target_date=None):
        """
        Retorna os horários das doses previstas para uma data.
        O intervalo é contínuo, inclusive entre dias diferentes.
        """
        if target_date is None:
            target_date = date.today()

        if target_date < self.begin or (self.end and target_date > self.end):
            return []

        if not self.take_at:
            return []

        weekdays = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

        selected_days = (
            [day.strip() for day in self.days.split(",") if day.strip()]
            if self.days else None
        )

        def is_valid_day(dose_date):
            if selected_days is None:
                return True
            return weekdays[dose_date.weekday()] in selected_days

        # Uma dose por dia
        if self.cycle_type == "daily":
            return [self.take_at] if is_valid_day(target_date) else []

        # Doses em intervalos contínuos de horas
        if self.cycle_type == "interval":
            if not self.take_cycle or self.take_cycle <= 0:
                return []

            first_dose = datetime.combine(self.begin, self.take_at)
            day_start = datetime.combine(target_date, datetime.min.time())
            day_end = day_start + timedelta(days=1)

            schedules = []
            current_dose = first_dose

            while current_dose < day_end:
                dose_date = current_dose.date()

                if (
                    current_dose >= day_start
                    and (self.end is None or dose_date <= self.end)
                    and is_valid_day(dose_date)
                ):
                    schedules.append(current_dose.time())

                current_dose += timedelta(hours=self.take_cycle)

            return schedules

        return []


    def define_state(self):
        """Define o estado da dose com base no horário previsto."""

        now = timezone.now()
        current_now = timezone.localtime(now)
        current_time = current_now.time()

        schedules = self.calculate_schedule()

        if not schedules:
            return None

        # Identifica os horários que já deveriam ter acontecido.
        past_schedules = [
            scheduled_time
            for scheduled_time in schedules
            if scheduled_time <= current_time
        ]

        # Ainda não chegou o horário da dose.
        if not past_schedules:
            new_state = "waiting"
        else:
            # Pega o horário previsto mais próximo do horário atual.
            closest_scheduled_time = max(past_schedules)

            scheduled_datetime = datetime.combine(
                current_now.date(),
                closest_scheduled_time
            )

            scheduled_datetime = timezone.make_aware(
                scheduled_datetime,
                timezone.get_current_timezone()
            )

            time_gap = now - scheduled_datetime

            if time_gap > timedelta(minutes=30):
                new_state = "forgotten"
            elif time_gap > timedelta(minutes=10):
                new_state = "late"
            else:
                new_state = "taken"

        # Salva somente se o estado realmente mudou.
        if self.state != new_state:
            self.state = new_state
            self.save(update_fields=["state"])

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
            

    def get_scheduled_times(self, target_date):
        """
        Retorna os horários previstos para uma data específica.
        Os intervalos são contínuos, inclusive atravessando a meia-noite.
        """

        if target_date < self.begin or (self.end and target_date > self.end):
            return []

        if not self.take_at:
            return []

        weekdays = [
            "mon", "tue", "wed",
            "thu", "fri", "sat", "sun"
        ]

        selected_days = (
            [day.strip().lower() for day in self.days.split(",") if day.strip()]
            if self.days
            else None
        )

        def is_valid_day(dose_date):
            if selected_days is None:
                return True

            return weekdays[dose_date.weekday()] in selected_days

        # Uma dose por dia.
        if self.cycle_type == "daily":
            return [self.take_at] if is_valid_day(target_date) else []

        # Doses em intervalos contínuos.
        if self.cycle_type == "interval":
            if not self.take_cycle or self.take_cycle <= 0:
                return []

            first_dose = datetime.combine(
                self.begin,
                self.take_at
            )

            day_start = datetime.combine(
                target_date,
                time.min
            )

            day_end = day_start + timedelta(days=1)

            schedules = []
            current_dose = first_dose

            while current_dose < day_end:
                dose_date = current_dose.date()

                if (
                    current_dose >= day_start
                    and self.begin <= dose_date and (self.end is None or dose_date <= self.end)
                    and is_valid_day(dose_date)
                ):
                    schedules.append(current_dose.time())

                current_dose += timedelta(hours=self.take_cycle)

            return schedules

        return []
    def __str__(self):
            horarios = ", ".join([t.strftime('%H:%M') for t in self.calculate_schedule()])
            return f"{self.taken_id} - Horários: {horarios}"