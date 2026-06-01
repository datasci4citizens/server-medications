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
from datetime import date, time, datetime, timedelta
from django.utils import timezone
from django.test import TestCase
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
    
    def test_advance_the_medication(self):
        from django.core.exceptions import ValidationError

        scheduled = time(9, 0)
        now_time  = time(8, 0)  # 60 min before

        rec = self._make_record(scheduled)
        with patch("medication.models.timezone.now",
                return_value=self._fake_now(now_time)):
            with self.assertRaises(ValidationError):
                rec.define_state()
    
    def test_within_window_does_not_raise(self):
        from django.core.exceptions import ValidationError

        scheduled = time(9, 0)
        now_time  = time(8, 55)  # 5 min before

        rec = self._make_record(scheduled)
        with patch("medication.models.timezone.now",
                return_value=self._fake_now(now_time)):
            try:
                rec.define_state()
            except ValidationError:
                self.fail("define_state lançou ValidationError dentro da janela permitida.")

                
    def test_forgotten_after_10_min(self):
        """Mais de 30 min de atraso → estado 'forgotten'."""
        scheduled = time(8, 0)
        now_time  = time(9, 0)

        rec = self._make_record(scheduled)
        with patch("medication.models.timezone.now",
                   return_value=self._fake_now(now_time)):
            state = rec.define_state()

        self.assertEqual(state, "forgotten")

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

# Testes: TakeRecord.check_medication_day

class TestCheckMedicationDay(unittest.TestCase):
    """
    Testa se o usuário está tentando marcar uma medicação
    em um dia diferente do dia atual.
    """

    def _make_record(self):
        take = MagicMock()
        take.quantity = "30"
        take.med_format = "pílula"
        return make_take_record(take, take_at=time(8, 0))

    def test_today_does_not_raise(self):
        from django.core.exceptions import ValidationError
        rec = self._make_record()
        try:
            rec.check_medication_day(selected_date=date.today())
        except ValidationError:
            self.fail("check_medication_day lançou ValidationError para a data de hoje.")

    def test_past_date_raises_validation_error(self):
        from django.core.exceptions import ValidationError
        rec = self._make_record()
        yesterday = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            rec.check_medication_day(selected_date=yesterday)

    def test_future_date_raises_validation_error(self):
        from django.core.exceptions import ValidationError
        rec = self._make_record()
        tomorrow = date.today() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            rec.check_medication_day(selected_date=tomorrow)

    def test_error_message_contains_dates(self):
        from django.core.exceptions import ValidationError
        rec = self._make_record()
        wrong_date = date.today() - timedelta(days=3)
        with self.assertRaises(ValidationError) as ctx:
            rec.check_medication_day(selected_date=wrong_date)
        
        error_message = str(ctx.exception)
        self.assertIn(wrong_date.strftime('%d/%m/%Y'), error_message)
        self.assertIn(date.today().strftime('%d/%m/%Y'), error_message)

    def test_none_defaults_to_today(self):
        """selected_date=None deve usar date.today() e não lançar exceção."""
        from django.core.exceptions import ValidationError
        rec = self._make_record()
        try:
            rec.check_medication_day(selected_date=None)
        except ValidationError:
            self.fail("check_medication_day lançou ValidationError quando selected_date=None.")

# alarm

class TestAlarm(unittest.TestCase):
    """
    Testa se alarm() agenda corretamente os horários no Schedule do Django-Q.
    """

    def _make_record(self, **kwargs):
        take = MagicMock()
        take.quantity = "30"
        take.med_format = "pílula"
        rec = make_take_record(take, **kwargs)
        rec.pk = 99  # pk fixo para checar o nome do Schedule
        return rec

    @patch('medication.models.Schedule.objects.get_or_create')
    @patch('medication.models.timezone.now')
    def test_alarm_schedules_daily(self, mock_now, mock_get_or_create):
        """Ciclo diário → cria 1 agendamento no Schedule."""
        today = date.today()
        fake_now = timezone.make_aware(datetime.combine(today, time(7, 0)))
        mock_now.return_value = fake_now

        rec = self._make_record(cycle_type='daily', take_at=time(8, 0))
        rec.alarm()

        self.assertEqual(mock_get_or_create.call_count, 1)

        call_kwargs = mock_get_or_create.call_args
        self.assertIn('alarme_takerecord_99_0800', call_kwargs[1]['name'] 
                      if 'name' in call_kwargs[1] 
                      else call_kwargs[0][0])

    @patch('medication.models.Schedule.objects.get_or_create')
    @patch('medication.models.timezone.now')
    def test_alarm_schedules_interval_8h(self, mock_now, mock_get_or_create):
        """Ciclo 8h a partir das 00:00 → cria 3 agendamentos."""
        today = date.today()
        fake_now = timezone.make_aware(datetime.combine(today, time(0, 0)))
        mock_now.return_value = fake_now

        rec = self._make_record(
            cycle_type='interval',
            take_at=time(0, 0),
            take_cycle=8
        )
        rec.alarm()

        self.assertEqual(mock_get_or_create.call_count, 3)

    @patch('medication.models.Schedule.objects.get_or_create')
    @patch('medication.models.timezone.now')
    def test_alarm_skips_past_schedules(self, mock_now, mock_get_or_create):
        """Horários que já passaram não devem ser agendados."""
        today = date.today()
        fake_now = timezone.make_aware(datetime.combine(today, time(17, 0)))
        mock_now.return_value = fake_now

        rec = self._make_record(
            cycle_type='interval',
            take_at=time(6, 0),
            take_cycle=8
        )
        rec.alarm()

        self.assertEqual(mock_get_or_create.call_count, 1)

    @patch('medication.models.Schedule.objects.get_or_create')
    @patch('medication.models.timezone.now')
    def test_alarm_no_schedules_does_nothing(self, mock_now, mock_get_or_create):
        """Sem take_at → alarm() não cria nenhum agendamento."""
        rec = self._make_record(cycle_type='daily', take_at=None)
        rec.alarm()

        mock_get_or_create.assert_not_called()

    @patch('medication.models.Schedule.objects.get_or_create')
    @patch('medication.models.timezone.now')
    def test_alarm_unique_name_per_time(self, mock_now, mock_get_or_create):
        """Cada horário gera um nome único no Schedule para evitar duplicatas."""
        today = date.today()
        fake_now = timezone.make_aware(datetime.combine(today, time(0, 0)))
        mock_now.return_value = fake_now

        rec = self._make_record(
            cycle_type='interval',
            take_at=time(0, 0),
            take_cycle=12  # 00:00 e 12:00
        )
        rec.alarm()

        names = [
            call[1].get('name', call[0][0] if call[0] else '')
            for call in mock_get_or_create.call_args_list
        ]

        self.assertEqual(len(set(names)), 2)


class TestNotifyUser(unittest.TestCase):
    """
    Testa se notify_user() busca corretamente o nome do medicamento.
    """

    def _make_full_record(self, med_name=None):
        """Cria um TakeRecord com toda a cadeia de FKs mockada."""
        # Monta Medication_Name
        med_name_obj = MagicMock()
        med_name_obj.name = med_name or "Dipirona"

        # Monta Medication
        medication = MagicMock()
        medication.medication_id = 1
        medication.name.first.return_value = med_name_obj

        # Monta Take
        take = MagicMock()
        take.medication_id = medication
        take.quantity = "30"
        take.med_format = "pílula"

        # Monta TakeRecord
        rec = MagicMock()
        rec.pk = 99
        rec.taken_id = take

        return rec

    @patch('medication.tasks.TakeRecord')
    def test_notify_user_prints_medication_name(self, mock_takerecord_class):
        """notify_user deve encontrar e usar o nome do medicamento."""
        from medication.tasks import notify_user

        rec = self._make_full_record(med_name="Dipirona")
        mock_takerecord_class.objects.get.return_value = rec

        with patch('builtins.print') as mock_print:
            notify_user(99)
            mock_print.assert_called_once_with("Hora de tomar: Dipirona")

    @patch('medication.tasks.TakeRecord')
    def test_notify_user_fallback_when_no_name(self, mock_takerecord_class):
        """Se não houver Medication_Name, usa o medication_id como fallback."""
        from medication.tasks import notify_user

        rec = self._make_full_record()
        rec.taken_id.medication_id.name.first.return_value = None  # sem nome cadastrado
        mock_takerecord_class.objects.get.return_value = rec

        with patch('builtins.print') as mock_print:
            notify_user(99)
            # deve usar o fallback com medication_id
            printed = mock_print.call_args[0][0]
            self.assertIn("medicamento", printed)

    @patch('medication.tasks.TakeRecord')
    def test_notify_user_calls_correct_record(self, mock_takerecord_class):
        """notify_user deve buscar o TakeRecord pelo id correto."""
        from medication.tasks import notify_user

        rec = self._make_full_record()
        mock_takerecord_class.objects.get.return_value = rec

        notify_user(99)

        mock_takerecord_class.objects.get.assert_called_once_with(pk=99)

# get medication by date


def _make_medication(pk=1):
    med = MagicMock()
    med.pk = pk
    return med


def _make_person(pk=1):
    person = MagicMock()
    person.pk = pk
    return person


def _make_take(pk=1, person=None, medication=None, med_format="pílula", quantity="30"):
    take = MagicMock()
    take.pk = pk
    take.person_id = person or _make_person()
    take.medication_id = medication or _make_medication()
    take.med_format = med_format
    take.quantity = quantity
    return take


def _make_record(pk=1, take=None, cycle_type="daily", take_at=time(8, 0),
                 take_cycle=None, days="mon,tue,wed,thu,fri,sat,sun",
                 begin=None, end=None):
    """Cria um TakeRecord fake com calculate_schedule() real."""
    from medication.models import TakeRecord  # importação real para usar o método

    record = MagicMock(spec=TakeRecord)
    record.pk = pk
    record.taken_id = take or _make_take()
    record.cycle_type = cycle_type
    record.take_at = take_at
    record.take_cycle = take_cycle
    record.days = days
    record.begin = begin or date.today() - timedelta(days=5)
    record.end = end or date.today() + timedelta(days=25)

    # Usa a implementação real de calculate_schedule
    record.calculate_schedule.side_effect = lambda: TakeRecord.calculate_schedule(record)

    return record



class GetMedicationsByDateTest(TestCase):
    """Testes para TakeRecord.get_medications_by_date()"""

    def _call(self, record, person_id, selected_date=None):
        """Chama o método real passando o record como self."""
        from medication.models import TakeRecord
        return TakeRecord.get_medications_by_date(record, person_id, selected_date)


    # 1. Retorna medicamento quando o dia da semana bate
    
    @patch("medication.models.TakeRecord.objects")
    def test_retorna_medicamento_no_dia_correto(self, mock_qs):
        """Deve retornar o medicamento quando o dia selecionado está em record.days."""
        today = date.today()
        day_map = {0:"mon",1:"tue",2:"wed",3:"thu",4:"fri",5:"sat",6:"sun"}
        day_key = day_map[today.weekday()]

        record = _make_record(days=day_key)
        mock_qs.filter.return_value = [record]

        result = self._call(record, person_id=1, selected_date=today)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["medication"], record.taken_id.medication_id)
        self.assertIsInstance(result[0]["schedules"], list)
        self.assertGreater(len(result[0]["schedules"]), 0)


    # 2. Não retorna medicamento quando o dia não está em record.days
    
    @patch("medication.models.TakeRecord.objects")
    def test_nao_retorna_medicamento_dia_errado(self, mock_qs):

        today = date.today()
        all_days = {"mon","tue","wed","thu","fri","sat","sun"}
        day_map = {0:"mon",1:"tue",2:"wed",3:"thu",4:"fri",5:"sat",6:"sun"}
        today_key = day_map[today.weekday()]

        other_days = ",".join(all_days - {today_key})
        record = _make_record(days=other_days)
        mock_qs.filter.return_value = [record]

        result = self._call(record, person_id=1, selected_date=today)

        self.assertEqual(result, [])


    # 3. Usa date.today() quando selected_date não é informado
    
    @patch("medication.models.TakeRecord.objects")
    def test_usa_today_quando_sem_data(self, mock_qs):
        """Quando selected_date=None, deve usar a data de hoje."""
        today = date.today()
        day_map = {0:"mon",1:"tue",2:"wed",3:"thu",4:"fri",5:"sat",6:"sun"}
        day_key = day_map[today.weekday()]

        record = _make_record(days=day_key)
        mock_qs.filter.return_value = [record]

        result = self._call(record, person_id=1, selected_date=None)

        # Verifica que o filtro foi chamado com a data de hoje
        call_kwargs = mock_qs.filter.call_args[1]
        self.assertEqual(call_kwargs["begin__lte"], today)
        self.assertEqual(call_kwargs["end__gte"], today)


    # 4. Retorna lista vazia quando não há registros no QuerySet
    
    @patch("medication.models.TakeRecord.objects")
    def test_retorna_vazio_sem_registros(self, mock_qs):
        """Deve retornar lista vazia quando o QuerySet não tem resultados."""
        mock_qs.filter.return_value = []
        record = _make_record()

        result = self._call(record, person_id=1, selected_date=date.today())

        self.assertEqual(result, [])


    # 5. Filtra pelo person_id correto
    
    @patch("medication.models.TakeRecord.objects")
    def test_filtra_por_person_id(self, mock_qs):
        """O QuerySet deve ser filtrado pelo person_id informado."""
        mock_qs.filter.return_value = []
        record = _make_record()

        self._call(record, person_id=42, selected_date=date.today())

        call_kwargs = mock_qs.filter.call_args[1]
        self.assertEqual(call_kwargs["taken_id__person_id"], 42)


    # 6. Retorna múltiplos medicamentos no mesmo dia
    
    @patch("medication.models.TakeRecord.objects")
    def test_retorna_multiplos_medicamentos(self, mock_qs):
        """Deve retornar todos os medicamentos programados para o dia."""
        today = date.today()
        day_map = {0:"mon",1:"tue",2:"wed",3:"thu",4:"fri",5:"sat",6:"sun"}
        day_key = day_map[today.weekday()]

        record1 = _make_record(pk=1, days=day_key, take_at=time(8, 0))
        record2 = _make_record(pk=2, days=day_key, take_at=time(14, 0))
        mock_qs.filter.return_value = [record1, record2]

        result = self._call(record1, person_id=1, selected_date=today)

        self.assertEqual(len(result), 2)


    # 7. Horários calculados para ciclo de intervalo (8/8 horas)
    
    @patch("medication.models.TakeRecord.objects")
    def test_horarios_ciclo_intervalo(self, mock_qs):
        """Para cycle_type='interval' de 8h, deve retornar 3 horários no dia."""
        today = date.today()
        day_map = {0:"mon",1:"tue",2:"wed",3:"thu",4:"fri",5:"sat",6:"sun"}
        day_key = day_map[today.weekday()]

        record = _make_record(
            days=day_key,
            cycle_type="interval",
            take_at=time(6, 0),
            take_cycle=8,
        )
        mock_qs.filter.return_value = [record]

        result = self._call(record, person_id=1, selected_date=today)

        self.assertEqual(len(result), 1)
        schedules = result[0]["schedules"]
        # 06:00, 14:00, 22:00  →  3 horários
        self.assertEqual(len(schedules), 3)
        self.assertEqual(schedules[0], time(6, 0))
        self.assertEqual(schedules[1], time(14, 0))
        self.assertEqual(schedules[2], time(22, 0))


    # 8. Data fora do intervalo begin/end não é retornada
    
    @patch("medication.models.TakeRecord.objects")
    def test_fora_do_periodo_nao_retornado(self, mock_qs):
        """Registros fora do período begin-end não devem aparecer (filtro do ORM)."""
        # O próprio ORM não retornará o registro; simulamos QuerySet vazio
        mock_qs.filter.return_value = []
        record = _make_record(
            begin=date.today() + timedelta(days=5),
            end=date.today() + timedelta(days=10),
        )

        result = self._call(record, person_id=1, selected_date=date.today())

        self.assertEqual(result, [])


    # 9. Data passada válida (histórico)
    
    @patch("medication.models.TakeRecord.objects")
    def test_data_passada_valida(self, mock_qs):
        """Deve funcionar corretamente para datas passadas dentro do período."""
        past_date = date.today() - timedelta(days=3)
        day_map = {0:"mon",1:"tue",2:"wed",3:"thu",4:"fri",5:"sat",6:"sun"}
        day_key = day_map[past_date.weekday()]

        record = _make_record(days=day_key)
        mock_qs.filter.return_value = [record]

        result = self._call(record, person_id=1, selected_date=past_date)

        self.assertEqual(len(result), 1)


    # 10. Estrutura de retorno contém as chaves esperadas
    
    @patch("medication.models.TakeRecord.objects")
    def test_estrutura_retorno(self, mock_qs):
        """Cada item da lista deve ter as chaves 'medication' e 'schedules'."""
        today = date.today()
        day_map = {0:"mon",1:"tue",2:"wed",3:"thu",4:"fri",5:"sat",6:"sun"}
        day_key = day_map[today.weekday()]

        record = _make_record(days=day_key)
        mock_qs.filter.return_value = [record]

        result = self._call(record, person_id=1, selected_date=today)

        self.assertIn("medication", result[0])
        self.assertIn("schedules", result[0])























if __name__ == "__main__":
    unittest.main(verbosity=2)