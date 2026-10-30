import os

import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings


def get_firebase_app():
    """
    Inicializa o Firebase apenas uma vez.
    """
    if firebase_admin._apps:
        return firebase_admin.get_app()

    credentials_path = os.getenv("FCM_CREDENTIALS_PATH")

    if not credentials_path:
        raise RuntimeError(
            "FCM_CREDENTIALS_PATH não foi configurado no .env"
        )

    if not os.path.isfile(credentials_path):
        raise FileNotFoundError(
            "Arquivo de credenciais do Firebase não encontrado."
        )

    credential = credentials.Certificate(credentials_path)

    return firebase_admin.initialize_app(credential)


def send_push_notification(device, title, body, data=None):
    """
    Envia uma notificação para um dispositivo.
    """
    get_firebase_app()

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data={
            str(key): str(value)
            for key, value in (data or {}).items()
        },
        token=device.fcm_token,
    )

    return messaging.send(message)
