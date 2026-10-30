from rest_framework import serializers
from .models import Device


class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = [
            "id",
            "fcm_token",
            "platform",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "active",
            "created_at",
            "updated_at",
        ]

    def validate_fcm_token(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "O token FCM não pode ser vazio."
            )
        return value