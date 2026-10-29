from django.urls import path, include
from .views import PersonViewSet, DrugView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('persons', PersonViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('drugs', DrugView.as_view())
]