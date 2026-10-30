from datetime import date, datetime, timedelta

from django.db import IntegrityError
from django.utils import timezone

from .models import NotificationLog
from medication.models import TakeRecord

from .models import Device
from .services import send_push_notification

def generate_notification_logs():
    """
    Gera os registros de lembretes para hoje e amanhã.

    A restrição unique de NotificationLog impede
    a criação duplicada do mesmo lembrete.
    """
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)

    records = TakeRecord.objects.filter(
        begin__lte=tomorrow,
        end__gte=today,
    ).select_related("taken_id")

    created_count = 0

    for record in records:
        for target_date in (today, tomorrow):

            schedules = record.calculate_schedule(target_date)

            for scheduled_time in schedules:
                scheduled_datetime = datetime.combine(
                    target_date,
                    scheduled_time,
                )

                scheduled_datetime = timezone.make_aware(
                    scheduled_datetime,
                    timezone.get_current_timezone(),
                )

                try:
                    log, created = NotificationLog.objects.get_or_create(
                        take_record=record,
                        scheduled_for=scheduled_datetime,
                    )

                    if created:
                        created_count += 1

                except IntegrityError:
                    # Outro processo pode ter criado o mesmo registro.
                    continue

    return created_count


def process_pending_notifications():
    """
    Envia notificações pendentes que chegaram ao horário.
    """
    now = timezone.now()
    minimum_time = now - timedelta(minutes=5)

    pending_logs = NotificationLog.objects.filter(
        status="pending",
        scheduled_for__lte=now,
        scheduled_for__gte=minimum_time,
    ).select_related(
        "take_record__taken_id"
    ).order_by("scheduled_for")

    sent_count = 0
    failed_count = 0

    for log in pending_logs:

        # Marca como em processamento antes do envio.
        log.status = "sending"
        log.attempt_count += 1
        log.last_attempt_at = now
        log.save(
            update_fields=[
                "status",
                "attempt_count",
                "last_attempt_at",
                "updated_at",
            ]
        )

        # Localiza o paciente relacionado ao TakeRecord.
        take = log.take_record.taken_id
        person = take.person_id

        devices = Device.objects.filter(
            person=person,
            active=True,
        )

        if not devices.exists():
            log.status = "failed"
            log.error_message = "Nenhum dispositivo ativo cadastrado."
            log.save(
                update_fields=[
                    "status",
                    "error_message",
                    "updated_at",
                ]
            )
            failed_count += 1
            continue

        successful_sends = 0
        errors = []

        for device in devices:
            try:
                send_push_notification(
                    device=device,
                    title="Lembrete de medicamento",
                    body="Está na hora de tomar sua dose programada.",
                    data={
                        "notification_log_id": log.pk,
                        "take_record_id": log.take_record_id,
                    },
                )

                successful_sends += 1

            except Exception as error:
                errors.append(
                    f"Dispositivo {device.pk}: {str(error)}"
                )

        if successful_sends > 0:
            log.status = "sent"
            log.sent_at = timezone.now()
            log.error_message = "\n".join(errors)
            sent_count += 1

        else:
            log.status = "failed"
            log.error_message = "\n".join(errors)
            failed_count += 1

        log.save(
            update_fields=[
                "status",
                "sent_at",
                "error_message",
                "updated_at",
            ]
        )

    return {
        "sent": sent_count,
        "failed": failed_count,
    }
