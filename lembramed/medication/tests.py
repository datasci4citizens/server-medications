"""
tests.py — Testes unitários para as funções:
  - Take.check_interactions
  - TakeRecord.calculate_schedule
  - TakeRecord.define_state
  - TakeRecord.calculate_stock

Como o Interactions.json ainda não é a versão final, os testes usam
unittest.mock.patch para substituir a leitura do arquivo por dados
controlados definidos aqui mesmo.
"""

import json
import os
import unittest
from datetime import date, time, datetime, timedelta
from unittest.mock import MagicMock, patch, mock_open

# Helpers para criar objetos fake sem banco de dados

def make_medication(med_id, ingredients):
    """Cria um Medication fake com active_ingredient QuerySet simulado."""
    med = MagicMock()
    med.pk = med_id

    # ingredient.values_list('active_ingredient', flat=True)  → lista de strings
    ingredient_qs = MagicMock()
    ingredient_qs.values_list.return_value = ingredients
    med.ingredient = ingredient_qs
    return med


def make_person(person_id=1):
    person = MagicMock()
    person.pk = person_id
    return person


def make_take(person, medication, quantity="30", med_format="pílula"):
    """
    Cria uma instância de Take sem tocar no banco.

    Usa Model._default_manager.model() seria mais limpo, mas exigiria DB.
    A saída correta sem DB é:
      1. __new__ para pular __init__ (que tentaria acessar o banco)
      2. _state precisa existir com fields_cache, pois os descriptors de FK
         do Django sempre acessam instance._state.fields_cache
      3. Os FKs são guardados no fields_cache do _state, não em __dict__,
         para que o descriptor os encontre corretamente.
    """
    from django.db.models.base import ModelState
    from medication.models import Take

    take = Take.__new__(Take)
    take._state = ModelState()          

    take.pk       = None
    take.quantity = quantity
    take.med_format  = med_format

    # Guarda os objetos relacionados no fields_cache do _state
    # (é exatamente onde o descriptor de FK procura ao fazer get_cached_value)
    take._state.fields_cache["person_id"]     = person
    take._state.fields_cache["medication_id"] = medication

    return take



def make_take_record(take, cycle_type='daily', begin=None, end=None, take_at=None, take_cycle=None, state=None, med_format="pílula"):
    """
    Cria TakeRecord fake sem banco.

    Mesma estratégia de make_take: inicializa _state e guarda o FK
    relacionado no fields_cache para que o descriptor o encontre.
    """
    from django.db.models.base import ModelState
    from medication.models import TakeRecord

    rec = TakeRecord.__new__(TakeRecord)
    rec._state = ModelState()           # inicializa _state com fields_cache vazio

    # Guarda o objeto Take relacionado no fields_cache
    rec._state.fields_cache["taken_id"] = take

    rec.cycle_type = cycle_type
    rec.begin      = begin or date.today()
    rec.end        = end   or (date.today() + timedelta(days=30))
    rec.take_at    = take_at
    rec.take_cycle = take_cycle
    rec.state      = state
    rec.days       = 'mon,tue,wed,thu,fri'
    return rec



# Testes: TakeRecord.calculate_schedule

class TestCalculateSchedule(unittest.TestCase):
    """
    Testa o cálculo dos horários de tomada do medicamento.
    """

    def _make_record(self, **kwargs):
        take = MagicMock()
        take.quantity = "30"
        take.med_format  = "pílula"
        return make_take_record(take, **kwargs)

    def test_daily_single_time(self):
        """Ciclo diário → retorna exatamente 1 horário."""
        rec = self._make_record(cycle_type='daily', take_at=time(8, 0))
        schedule = rec.calculate_schedule()
        self.assertEqual(schedule, [time(8, 0)])

    def test_no_take_at_returns_empty(self):
        """Sem take_at → lista vazia."""
        rec = self._make_record(cycle_type='daily', take_at=None)
        self.assertEqual(rec.calculate_schedule(), [])

    def test_interval_8h(self):
        """Intervalo de 8h a partir das 00:00 → 3 horários no dia."""
        rec = self._make_record(
            cycle_type='interval',
            take_at=time(0, 0),
            take_cycle=8
        )
        schedule = rec.calculate_schedule()
        self.assertEqual(schedule, [time(0, 0), time(8, 0), time(16, 0)])

    def test_interval_6h(self):
        """Intervalo de 6h a partir das 00:00 → 4 horários no dia."""
        rec = self._make_record(
            cycle_type='interval',
            take_at=time(0, 0),
            take_cycle=6
        )
        schedule = rec.calculate_schedule()
        self.assertEqual(len(schedule), 4)
        self.assertEqual(schedule[0], time(0, 0))
        self.assertEqual(schedule[-1], time(18, 0))

    def test_interval_12h(self):
        """Intervalo de 12h a partir das 08:00 → 2 horários."""
        rec = self._make_record(
            cycle_type='interval',
            take_at=time(8, 0),
            take_cycle=12
        )
        schedule = rec.calculate_schedule()
        self.assertEqual(schedule, [time(8, 0), time(20, 0)])

    def test_interval_without_take_cycle(self):
        """interval sem take_cycle → lista vazia."""
        rec = self._make_record(
            cycle_type='interval',
            take_at=time(8, 0),
            take_cycle=None
        )
        self.assertEqual(rec.calculate_schedule(), [])

    def test_interval_starting_midday(self):
        """Intervalo 8h a partir das 12:00 → horários que não ultrapassam meia-noite."""
        rec = self._make_record(
            cycle_type='interval',
            take_at=time(12, 0),
            take_cycle=8
        )
        schedule = rec.calculate_schedule()
        # 12:00 e 20:00 cabem; 28:00 extrapola
        self.assertEqual(schedule, [time(12, 0), time(20, 0)])


#  Testes: TakeRecord.define_state

class TestDefineState(unittest.TestCase):
    """
    Testa a definição de estado (taken / late / forgotten / waiting)
    baseado no horário atual vs. horário agendado.
    """

    def _make_record(self, take_at, cycle_type='daily', take_cycle=None):
        take = MagicMock()
        take.quantity = "30"
        take.med_format  = "pílula"
        rec = make_take_record(take, cycle_type=cycle_type,
                               take_at=take_at, take_cycle=take_cycle)
        rec.save = MagicMock()       # evita chamada ao banco
        return rec

    def _fake_now(self, t: time):
        """Cria um datetime aware com o horário desejado para hoje."""
        from django.utils import timezone as tz
        today = date.today()
        naive = datetime.combine(today, t)
        return tz.make_aware(naive)

    def test_taken_within_window(self):
        """Tomado dentro de 10 min após o horário → estado 'taken'."""
        scheduled = time(8, 0)
        now_time  = time(8, 5)

        rec = self._make_record(scheduled)
        with patch("medication.models.timezone.now",
                   return_value=self._fake_now(now_time)):
            state = rec.define_state()

        self.assertEqual(state, "taken")

    def test_forgotten_after_10_min(self):
        """Mais de 30 min de atraso → estado 'forgotten'."""
        scheduled = time(8, 0)
        now_time  = time(9, 0)

        rec = self._make_record(scheduled)
        with patch("medication.models.timezone.now",
                   return_value=self._fake_now(now_time)):
            state = rec.define_state()

        self.assertEqual(state, "forgotten")

    def test_waiting_before_first_schedule(self):
        """Horário atual antes do primeiro agendamento → 'waiting'."""
        scheduled = time(20, 0)
        now_time  = time(7, 0)

        rec = self._make_record(scheduled)
        with patch("medication.models.timezone.now",
                   return_value=self._fake_now(now_time)):
            state = rec.define_state()

        self.assertEqual(state, "waiting")

    def test_no_schedule_returns_none(self):
        """Sem take_at → define_state retorna None."""
        rec = self._make_record(take_at=None)
        rec.save = MagicMock()
        with patch("medication.models.timezone.now",
                   return_value=self._fake_now(time(10, 0))):
            state = rec.define_state()

        self.assertIsNone(state)


# Testes: TakeRecord.calculate_stock

class TestCalculateStock(unittest.TestCase):
    """
    Testa o cálculo de estoque e o aviso de reposição.
    """

    def _make_record(self, quantity, cycle_type='daily', take_cycle=None,
                     begin=None, end=None, days_passed=0, med_format="pílula"):
        take = MagicMock()
        take.quantity = str(quantity)
        take.med_format  = med_format

        today = date.today()
        rec = make_take_record(
            take,
            cycle_type=cycle_type,
            begin=today - timedelta(days=days_passed),
            end=end or (today + timedelta(days=60)),
            take_at=time(8, 0),
            take_cycle=take_cycle,
            med_format= med_format,
        )
        return rec

    def test_low_stock_daily_returns_warning(self):
        """
        Estoque baixo (< 7 doses) em ciclo diário com mais de 7 dias restantes
        → retorna mensagem de reposição.
        """
        rec = self._make_record(quantity=5, cycle_type='daily', days_passed=0)
        result = rec.calculate_stock()
        self.assertIsNotNone(result)
        self.assertIn("pílulas restantes", result)

    def test_sufficient_stock_daily_returns_none(self):
        """Estoque suficiente → retorna None (sem alerta)."""
        rec = self._make_record(quantity=30, cycle_type='daily', days_passed=0)
        result = rec.calculate_stock()
        self.assertIsNone(result)

    def test_low_stock_interval_8h(self):
        """
        Ciclo 8h (3 doses/dia) com pouco estoque e muito tempo restante
        → dispara aviso.
        """
        # 3 doses/dia × 7 dias = 21 doses/semana
        # quantity=15 < 21, end em 60 dias → deve avisar
        rec = self._make_record(
            quantity=15,
            cycle_type='interval',
            take_cycle=8,
            days_passed=0,
        )
        result = rec.calculate_stock()
        self.assertIsNotNone(result)
        self.assertIn("pílulas restantes", result)

    def test_non_pill_format_returns_none(self):
        """Formato diferente de 'pílula' → retorna None (não implementado)."""
        rec = self._make_record(quantity=5, cycle_type='daily',
                                days_passed=0, med_format="xarope")
        result = rec.calculate_stock()
        self.assertIsNone(result)

    def test_invalid_quantity_returns_error_string(self):
        """Quantidade inválida → retorna string de erro."""
        rec = self._make_record(quantity="abc", cycle_type='daily', days_passed=0)
        result = rec.calculate_stock()
        self.assertIsNotNone(result)
        self.assertIn("Erro", result)

    def test_no_warning_when_treatment_ending_soon(self):
        """
        Pouco estoque MAS tratamento termina em ≤ 7 dias
        → não precisa repor, retorna None.
        """
        today = date.today()
        take = MagicMock()
        take.quantity = "3"
        take.med_format  = "pílula"

        rec = make_take_record(
            take,
            cycle_type='daily',
            begin=today - timedelta(days=25),
            end=today + timedelta(days=3),   # termina em 3 dias
            take_at=time(8, 0),
        )
        result = rec.calculate_stock()
        self.assertIsNone(result)

    def test_stock_decreases_with_days_passed(self):
        """
        Após vários dias de uso, a contagem de pílulas restantes diminui.
        """
        rec_day0 = self._make_record(quantity=30, cycle_type='daily', days_passed=0)
        rec_day10 = self._make_record(quantity=30, cycle_type='daily', days_passed=10)

        # Ambos não devem dar aviso ainda (stock ainda suficiente)
        # mas a lógica interna processa dias passados corretamente
        # Verificamos indiretamente: com 29 dias passados e 30 pílulas → 1 restante
        rec_almost_empty = self._make_record(
            quantity=30,
            cycle_type='daily',
            days_passed=29,
            end=date.today() + timedelta(days=30),  # ainda 30 dias restantes
        )
        result = rec_almost_empty.calculate_stock()
        self.assertIsNotNone(result)
        self.assertIn("1 pílulas restantes", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)