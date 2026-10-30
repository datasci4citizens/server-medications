from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status

from .models import Device
from .serializers import DeviceSerializer


class DeviceListCreateView(generics.ListCreateAPIView):

    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Device.objects.filter(
            person=self.request.user.person
        )

    def perform_create(self, serializer):
        serializer.save(
            person=self.request.user.person
        )


class DeviceDeactivateView(generics.UpdateAPIView):

    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Device.objects.filter(
            person=self.request.user.person
        )

    def update(self, request, *args, **kwargs):
        device = self.get_object()
        device.active = False
        device.save(update_fields=["active", "updated_at"])

        return Response(
            {"message": "Dispositivo desativado com sucesso."},
            status=status.HTTP_200_OK,
        )