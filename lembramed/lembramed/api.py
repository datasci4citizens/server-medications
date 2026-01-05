from rest_framework import routers, serializers, viewsets
from django.contrib.auth.models import User
from authentication.api import router as nome_app_router
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']
