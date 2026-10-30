from datetime import time
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient

from authentication.models import Person
from notifications.models import Device
from notifications.notification_processor import (
    generate_notification_logs,
    process_pending_notifications,
)
from notifications.services import send_push_notification


User = get_user_model()


class DeviceAPITests(TestCase):
    """Testa o cadastro, consulta e desativação de dispositivos."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="paciente_teste",
            email="paciente_teste@example.com",
            password="senha_teste_123",
        )

        # Garante que o perfil Person exista.
        self.person, _ = Person.objects.get_or_create(
            user=self.user
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.url = "/notifications/devices/"

    def test_cadastrar_dispositivo(self):
        response = self.client.post(
            self.url,
            {
                "fcm_token": "token_fcm_teste_001",
                "platform": "android",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        device = Device.objects.get(
            fcm_token="token_fcm_teste_001"
        )

        self.assertEqual(device.person, self.person)
        self.assertEqual(device.platform, "android")
        self.assertTrue(device.active)

    def test_listar_apenas_dispositivos_do_paciente(self):
        outro_user = User.objects.create_user(
            username="outro_paciente",
            password="senha_teste_123",
        )
        outro_person, _ = Person.objects.get_or_create(
            user=outro_user
        )

        Device.objects.create(
            person=self.person,
            fcm_token="token_do_paciente",
            platform="android",
        )

        Device.objects.create(
            person=outro_person,
            fcm_token="token_de_outra_pessoa",
            platform="ios",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["fcm_token"],
            "token_do_paciente",
        )

    def test_desativar_dispositivo(self):
        device = Device.objects.create(
            person=self.person,
            fcm_token="token_para_desativar",
            platform="android",
        )

        response = self.client.patch(
            f"{self.url}{device.pk}/deactivate/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        device.refresh_from_db()
        self.assertFalse(device.active)

    def test_paciente_nao_pode_desativar_dispositivo_de_outra_pessoa(self):
        outro_user = User.objects.create_user(
            username="outro_paciente_2",
            password="senha_teste_123",
        )
        outro_person, _ = Person.objects.get_or_create(
            user=outro_user
        )

        device = Device.objects.create(
            person=outro_person,
            fcm_token="token_privado",
            platform="ios",
        )

        response = self.client.patch(
            f"{self.url}{device.pk}/deactivate/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

        device.refresh_from_db()
        self.assertTrue(device.active)

    def test_nao_permite_cadastrar_sem_autenticacao(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url,
            {
                "fcm_token": "token_sem_login",
                "platform": "android",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)


class FirebaseServiceTests(TestCase):
    """Testa o serviço FCM sem acessar o Firebase real."""

    @patch("notifications.services.messaging.send")
    @patch("notifications.services.get_firebase_app")
    def test_envia_notificacao_simulada(
        self,
        mock_firebase,
        mock_send,
    ):
        mock_send.return_value = "mensagem-teste-123"

        device = SimpleNamespace(
            fcm_token="token_fcm_simulado"
        )

        result = send_push_notification(
            device=device,
            title="Lembrete de medicamento",
            body="Está na hora de tomar seu medicamento.",
            data={"take_record_id": 10},
        )

        self.assertEqual(result, "mensagem-teste-123")
        mock_firebase.assert_called_once()
        mock_send.assert_called_once()

        message = mock_send.call_args.args[0]

        self.assertEqual(
            message.notification.title,
            "Lembrete de medicamento",
        )
        self.assertEqual(
            message.token,
            "token_fcm_simulado",
        )


class NotificationGenerationTests(TestCase):
    """Testa a criação dos registros de lembretes."""

    @patch("notifications.notification_processor.NotificationLog.objects")
    @patch("notifications.notification_processor.TakeRecord.objects")
    def test_gera_registros_de_notificacao(
        self,
        mock_take_objects,
        mock_log_objects,
    ):
        record = MagicMock()
        record.calculate_schedule.return_value = [
            time(8, 0)
        ]

        mock_take_objects.filter.return_value.select_related.return_value = [
            record
        ]

        mock_log_objects.get_or_create.return_value = (
            MagicMock(),
            True,
        )

        result = generate_notification_logs()

        self.assertEqual(result, 2)
        self.assertEqual(
            mock_log_objects.get_or_create.call_count,
            2,
        )
        self.assertEqual(
            record.calculate_schedule.call_count,
            2,
        )

    @patch("notifications.notification_processor.NotificationLog.objects")
    @patch("notifications.notification_processor.TakeRecord.objects")
    def test_nao_conta_registros_ja_existentes(
        self,
        mock_take_objects,
        mock_log_objects,
    ):
        record = MagicMock()
        record.calculate_schedule.return_value = [
            time(8, 0)
        ]

        mock_take_objects.filter.return_value.select_related.return_value = [
            record
        ]

        mock_log_objects.get_or_create.return_value = (
            MagicMock(),
            False,
        )

        result = generate_notification_logs()

        self.assertEqual(result, 0)


class NotificationSendingTests(TestCase):
    """Testa o processamento dos lembretes sem Firebase real."""

    def create_fake_log(self):
        person = SimpleNamespace(pk=1)
        take = SimpleNamespace(person_id=person)
        take_record = SimpleNamespace(
            taken_id=take,
            pk=10,
        )

        log = MagicMock()
        log.pk = 20
        log.take_record = take_record
        log.take_record_id = 10

        return log

    @patch("notifications.notification_processor.send_push_notification")
    @patch("notifications.notification_processor.Device.objects")
    @patch("notifications.notification_processor.NotificationLog.objects")
    def test_notificacao_enviada_com_sucesso(
        self,
        mock_log_objects,
        mock_device_objects,
        mock_send,
    ):
        log = self.create_fake_log()

        device = SimpleNamespace(
            pk=1,
            fcm_token="token_simulado",
        )

        devices = MagicMock()
        devices.exists.return_value = True
        devices.__iter__.return_value = iter([device])

        mock_device_objects.filter.return_value = devices

        mock_log_objects.filter.return_value.select_related.return_value.order_by.return_value = [
            log
        ]

        mock_send.return_value = "mensagem-simulada"

        result = process_pending_notifications()

        self.assertEqual(result["sent"], 1)
        self.assertEqual(result["failed"], 0)

        self.assertEqual(log.status, "sent")
        self.assertIsNotNone(log.sent_at)
        mock_send.assert_called_once()

    @patch("notifications.notification_processor.Device.objects")
    @patch("notifications.notification_processor.NotificationLog.objects")
    def test_falha_quando_nao_existem_dispositivos(
        self,
        mock_log_objects,
        mock_device_objects,
    ):
        log = self.create_fake_log()

        devices = MagicMock()
        devices.exists.return_value = False

        mock_device_objects.filter.return_value = devices

        mock_log_objects.filter.return_value.select_related.return_value.order_by.return_value = [
            log
        ]

        result = process_pending_notifications()

        self.assertEqual(result["sent"], 0)
        self.assertEqual(result["failed"], 1)

        self.assertEqual(log.status, "failed")
        self.assertIn(
            "Nenhum dispositivo ativo",
            log.error_message,
        )

    @patch("notifications.notification_processor.send_push_notification")
    @patch("notifications.notification_processor.Device.objects")
    @patch("notifications.notification_processor.NotificationLog.objects")
    def test_falha_quando_firebase_retorna_erro(
        self,
        mock_log_objects,
        mock_device_objects,
        mock_send,
    ):
        log = self.create_fake_log()

        device = SimpleNamespace(
            pk=1,
            fcm_token="token_simulado",
        )

        devices = MagicMock()
        devices.exists.return_value = True
        devices.__iter__.return_value = iter([device])

        mock_device_objects.filter.return_value = devices

        mock_log_objects.filter.return_value.select_related.return_value.order_by.return_value = [
            log
        ]

        mock_send.side_effect = Exception(
            "Erro simulado no envio"
        )

        result = process_pending_notifications()

        self.assertEqual(result["sent"], 0)
        self.assertEqual(result["failed"], 1)

        self.assertEqual(log.status, "failed")
        self.assertIn(
            "Erro simulado no envio",
            log.error_message,
        )
