from . import views
from django.urls import path

urlpatterns = [
    path('', views.medication_list, name='medication_list'),
    path('add/', views.add_medication, name='add_medication'),
    path('delete/<int:id>/', views.delete_medication, name='delete_medication'),
]
