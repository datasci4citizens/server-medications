from django.urls import path
from .views import GoogleAuthView, UserView
from .views import RegisterView, LoginView, MeView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('me/',         MeView.as_view()),
    path('refresh/',    TokenRefreshView.as_view()),
    path('login/',      LoginView.as_view(),          name = 'login'),
    path('google/',     GoogleAuthView.as_view(),     name = 'google-auth'),
    path('register/',   RegisterView.as_view(),       name = 'create-user')
]