
from datetime import date, time, datetime, timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.utils import timezone

from medication.models import Take, TakeRecord


class CalculateScheduleTests(SimpleTestCase):
    """Testes dos horários calculados para cada tipo de ciclo."""

    def create_record(self, **kwargs):
        defaults = {
            "begin": date(2026, 10, 29),
            "end": date(2026, 11, 5),
            "cycle_type": "daily",
            "take_at": time(8, 0),
            "take_cycle": None,
            "days": None,
        }
        defaults.update(kwargs)
        return TakeRecord(**defaults)

    def test_daily_returns_one_time(self):
        record = self.create_record()

        self.assertEqual(
            record.calculate_schedule(date(2026, 10, 29)),
            [time(8, 0)]
        )

    def test_daily_respects_selected_weekdays(self):
        record = self.create_record(days="thu,sat")

        self.assertEqual(
            record.calculate_schedule(date(2026, 10, 29)),
            [time(8, 0)]
        )

    def test_daily_returns_empty_on_unselected_day(self):
        record = self.create_record(days="thu,sat")

        self.assertEqual(
            record.calculate_schedule(date(2026, 10, 30)),
            []
        )

    def test_interval_returns_times_during_same_day(self):
        record = self.create_record(
            cycle_type="interval",
            take_at=time(8, 0),
            take_cycle=6,
        )

        self.assertEqual(
            record.calculate_schedule(date(2026, 10, 29)),
            [time(8, 0), time(14, 0), time(20, 0)]
        )

    def test_interval_continues_after_midnight(self):
        record = self.create_record(
            cycle_type="interval",
            take_at=time(8, 0),
            take_cycle=6,
        )

        self.assertEqual(
            record.calculate_schedule(date(2026, 10, 30)),
            [time(2, 0), time(8, 0), time(14, 0), time(20, 0)]
        )

    def test_interval_starting_at_night(self):
        record = self.create_record(
            cycle_type="interval",
            take_at=time(22, 0),
            take_cycle=6,
        )

        self.assertEqual(
            record.calculate_schedule(date(2026, 10, 30)),
            [time(4, 0), time(10, 0), time(16, 0), time(22, 0)]
        )

    def test_returns_empty_before_begin_date(self):
        record = self.create_record()

        self.assertEqual(
            record.calculate_schedule(date(2026, 10, 28)),
            []
        )

    def test_returns_empty_after_end_date(self):
        record = self.create_record()

        self.assertEqual(
            record.calculate_schedule(date(2026, 11, 6)),
            []
        )

    def test_end_date_is_included(self):
        record = self.create_record(
            end=date(2026, 10, 30)
        )

        self.assertEqual(
            record.calculate_schedule(date(2026, 10, 30)),
            [time(8, 0)]
        )

    def test_interval_without_valid_cycle_returns_empty(self):
        record = self.create_record(
            cycle_type="interval",
            take_cycle=0,
        )

        self.assertEqual(
            record.calculate_schedule(date(2026, 10, 29)),
            []
        )

    def test_interval_respects_weekday_of_each_dose(self):
        record = self.create_record(
            cycle_type="interval",
            take_at=time(22, 0),
            take_cycle=6,
            days="fri",
        )

        self.assertEqual(
            record.calculate_schedule(date(2026, 10, 30)),
            [time(4, 0), time(10, 0), time(16, 0), time(22, 0)]
        )


class GetScheduledTimesTests(SimpleTestCase):
    """Testes do método get_scheduled_times."""

    def create_record(self, **kwargs):
        defaults = {
            "begin": date(2026, 10, 29),
            "end": date(2026, 11, 5),
            "cycle_type": "daily",
            "take_at": time(8, 0),
            "take_cycle": None,
            "days": None,
        }
        defaults.update(kwargs)
        return TakeRecord(**defaults)

    def test_daily_returns_one_time(self):
        record = self.create_record()

        self.assertEqual(
            record.get_scheduled_times(date(2026, 10, 29)),
            [time(8, 0)]
        )

    def test_returns_empty_before_begin(self):
        record = self.create_record()

        self.assertEqual(
            record.get_scheduled_times(date(2026, 10, 28)),
            []
        )

    def test_returns_empty_after_end(self):
        record = self.create_record()

        self.assertEqual(
            record.get_scheduled_times(date(2026, 11, 6)),
            []
        )

    def test_respects_selected_weekdays(self):
        record = self.create_record(days="thu,sat")

        self.assertEqual(
            record.get_scheduled_times(date(2026, 10, 30)),
            []
        )

    def test_interval_returns_expected_times(self):
        record = self.create_record(
            cycle_type="interval",
            take_at=time(8, 0),
            take_cycle=6,
        )

        self.assertEqual(
            record.get_scheduled_times(date(2026, 10, 29)),
            [time(8, 0), time(14, 0), time(20, 0)]
        )


class DefineStateTests(SimpleTestCase):
    """Testes da definição do estado da dose."""

    def create_record(self):
        return TakeRecord(
            begin=date(2026, 10, 29),
            end=date(2026, 10, 29),
            cycle_type="daily",
            take_at=time(10, 0),
        )

    def check_state_at(self, current_time):
        record = self.create_record()

        current_datetime = timezone.make_aware(
            datetime.combine(date(2026, 10, 29), current_time)
        )

        with (
            patch("medication.models.take_model.timezone.now",
                  return_value=current_datetime),
            patch.object(record, "calculate_schedule",
                         return_value=[time(10, 0)]),
            patch.object(record, "save") as mocked_save,
        ):
            result = record.define_state()

        mocked_save.assert_called_once()
        return result

    def test_state_is_waiting_before_scheduled_time(self):
        self.assertEqual(
            self.check_state_at(time(9, 0)),
            "waiting"
        )

    def test_state_is_taken_within_ten_minutes(self):
        self.assertEqual(
            self.check_state_at(time(10, 5)),
            "taken"
        )

    def test_state_is_late_after_ten_minutes(self):
        self.assertEqual(
            self.check_state_at(time(10, 15)),
            "late"
        )

    def test_state_is_forgotten_after_thirty_minutes(self):
        self.assertEqual(
            self.check_state_at(time(10, 40)),
            "forgotten"
        )

    def test_state_is_late_at_exactly_thirty_minutes(self):
        self.assertEqual(
            self.check_state_at(time(10, 30)),
            "late"
        )

    def test_returns_none_when_there_is_no_schedule(self):
        record = self.create_record()

        with patch.object(record, "calculate_schedule", return_value=[]):
            self.assertIsNone(record.define_state())


class TakeRecordValidationTests(SimpleTestCase):
    """Testes das validações do modelo."""

    def test_end_cannot_be_before_begin(self):
        record = TakeRecord(
            begin=date(2026, 10, 30),
            end=date(2026, 10, 29),
            cycle_type="daily",
            take_at=time(8, 0),
        )

        with self.assertRaises(ValidationError):
            record.clean()

    def test_daily_requires_take_at(self):
        record = TakeRecord(
            begin=date(2026, 10, 29),
            end=date(2026, 10, 30),
            cycle_type="daily",
            take_at=None,
        )

        with self.assertRaises(ValidationError):
            record.clean()

    def test_interval_requires_take_cycle(self):
        record = TakeRecord(
            begin=date(2026, 10, 29),
            end=date(2026, 10, 30),
            cycle_type="interval",
            take_at=time(8, 0),
            take_cycle=None,
        )

        with self.assertRaises(ValidationError):
            record.clean()

    def test_interval_requires_initial_time(self):
        record = TakeRecord(
            begin=date(2026, 10, 29),
            end=date(2026, 10, 30),
            cycle_type="interval",
            take_at=None,
            take_cycle=6,
        )

        with self.assertRaises(ValidationError):
            record.clean()

    def test_get_days_display(self):
        record = TakeRecord(days="mon,wed,fri")

        self.assertEqual(
            record.get_days_display(),
            "Segunda, Quarta, Sexta"
        )
