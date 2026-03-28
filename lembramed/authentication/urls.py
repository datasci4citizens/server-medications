from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, MeView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/',    LoginView.as_view()),
    path('refresh/',  TokenRefreshView.as_view()),  # renova o access token
    path('me/',       MeView.as_view()),
]