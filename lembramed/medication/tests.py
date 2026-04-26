from django.test import TestCase
from .models import Medication, Take, TakeRecord
from django.contrib.auth.models import User 
from django.utils import timezone
from datetime import time, timedelta, date
from freezegun import freeze_time # Importante para simular o horário

class MedicationLogicTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="teste@email.com", 
            email="teste@email.com", 
            password="password123"
        )
        self.person = self.user.person 
        self.med = Medication.objects.create(medication_id=100, name="Teste")
        
        self.take = Take.objects.create(
            person_id=self.person,
            medication_id=self.med,
            priority=1,
            quantity="30", # Total de pílulas no estoque
            formato="pílula"
        )

    def test_interval_schedule_calculation(self):
        record = TakeRecord.objects.create(
            taken_id=self.take,
            cycle_type='interval',
            take_at=time(10, 0),
            take_cycle=12
        )
        schedules = record.calculate_schedule()
        self.assertEqual(len(schedules), 2)

    def test_define_state_logic(self):
        """Testa se o estado muda corretamente conforme o tempo passa"""
        record = TakeRecord.objects.create(
            taken_id=self.take,
            cycle_type='daily',
            take_at=time(10, 0)
        )

        # Caso 1: 10:05 
        with freeze_time("2026-04-26 10:05:00"):
            self.assertEqual(record.define_state(), "taken")

        # Caso 2: 10:15 
        with freeze_time("2026-04-26 10:15:00"):
            self.assertEqual(record.define_state(), "late")

        # Caso 3: 10:40
        with freeze_time("2026-04-26 10:40:00"):
            self.assertEqual(record.define_state(), "forgotten")

    def test_calculate_stock_warning(self):
        """Testa o aviso de estoque baixo"""
        hoje = date.today()
        inicio = hoje - timedelta(days=25) # Começou há 25 dias
        fim = hoje + timedelta(days=10)    # Acaba em 10 dias

        record = TakeRecord.objects.create(
            taken_id=self.take,
            cycle_type='daily',
            begin=inicio,
            end=fim,
            take_at=time(10, 0)
        )

        resultado = record.calculate_stock()
        self.assertIn("reponha seu estoque", resultado)
        self.assertIn("5 pílulas restantes", resultado)