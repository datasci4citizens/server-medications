from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('add/', views.add_person, name='add_person'),
]
