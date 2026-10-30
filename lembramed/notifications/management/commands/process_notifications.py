
from django.core.management.base import BaseCommand

from notifications.notification_processor import (
    generate_notification_logs,
    process_pending_notifications,
)


class Command(BaseCommand):
    help = "Gera e envia os lembretes de medicamentos."

    def handle(self, *args, **options):
        created = generate_notification_logs()

        result = process_pending_notifications()

        self.stdout.write(
            self.style.SUCCESS(
                f"Processamento concluído. "
                f"Registros criados: {created}. "
                f"Enviados: {result['sent']}. "
                f"Falhas: {result['failed']}."
            )
        )
