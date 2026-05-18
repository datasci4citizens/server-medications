from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', PersonViewSet)
# router.register(r'leaflets', LeafletViewSet)
router.register(r'medication', MedicationViewSet)
# router.register(r'take', TakeViewSet)
urlpatterns = router.urls