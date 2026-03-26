from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonViewSet, MedicationViewSet, BulaViewSet



router = DefaultRouter()
router.register(r'users', PersonViewSet)
router.register(r'medications', MedicationViewSet)
router.register(r'bulas', BulaViewSet)
urlpatterns = router.urls