from .views import (
    MedicationViewSet, LeafletViewSet, 
    PresentationViewSet, AnvisaRegisterViewSet,
    TakeViewSet, TakeRecordViewSet,
    ingredientInteractionViewSet
)
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'leaflets',        LeafletViewSet,         basename="leaflet")
router.register(r'presentation',    PresentationViewSet,    basename="presentation")
router.register(r'anvisa_register', AnvisaRegisterViewSet,  basename="anvisa_register")

router.register(r'take',            TakeViewSet,            basename="take")
router.register(r'take_record',     TakeRecordViewSet,      basename="take_record")
router.register(r'ingredient_interaction', ingredientInteractionViewSet, basename="ingredient_interaction")
router.register(r'',                MedicationViewSet,      basename="medication") # /medication/...

urlpatterns = [
    path('', include(router.urls))
]
