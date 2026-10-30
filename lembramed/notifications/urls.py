from django.urls import path

from .views import (
    DeviceListCreateView,
    DeviceDeactivateView,
)

urlpatterns = [
    path(
        "devices/",
        DeviceListCreateView.as_view(),
        name="device-list-create",
    ),
    path(
        "devices/<int:pk>/deactivate/",
        DeviceDeactivateView.as_view(),
        name="device-deactivate",
    ),
]