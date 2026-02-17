from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonViewSet, MedicationViewSet



router = DefaultRouter()
router.register(r'users', PersonViewSet)
router.register(r'medications', MedicationViewSet)
urlpatterns = router.urls