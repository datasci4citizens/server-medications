from django.db import models


class Device(models.Model):
    """
    Armazena os dispositivos associados a uma pessoa
    e seus respectivos tokens do Firebase Cloud Messaging.
    """

    PLATFORM_CHOICES = [
        ("android", "Android"),
        ("ios", "iOS"),
        ("web", "Web"),
    ]

    person = models.ForeignKey(
        "authentication.Person",
        on_delete=models.CASCADE,
        related_name="devices",
    )

    fcm_token = models.TextField(unique=True)

    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
    )

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["person", "active"]),
        ]

    def __str__(self):
        return f"{self.person} - {self.platform}"


class NotificationLog(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sending", "Sending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    take_record = models.ForeignKey(
        "medication.TakeRecord",
        on_delete=models.CASCADE,
        related_name="notification_logs",
    )

    # Data e horário exatos em que o medicamento deveria ser tomado.
    scheduled_for = models.DateTimeField()

    # Data e horário em que a notificação foi enviada com sucesso.
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # Quantidade de tentativas de envio.
    attempt_count = models.PositiveIntegerField(default=0)

    # Última tentativa de envio.
    last_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # Descrição de eventual erro do Firebase.
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["take_record", "scheduled_for"],
                name="unique_take_record_notification",
            )
        ]

        indexes = [
            models.Index(fields=["status", "scheduled_for"]),
        ]

        ordering = ["-scheduled_for"]

    def __str__(self):
        return (
            f"TakeRecord {self.take_record_id} - "
            f"{self.scheduled_for} - {self.status}"
        )
