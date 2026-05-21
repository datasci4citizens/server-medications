from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Person


class RegisterSerializer(serializers.Serializer):
    email      = serializers.EmailField()
    first_name = serializers.CharField()
    last_name  = serializers.CharField()
    password   = serializers.CharField(write_only=True, min_length=8)
    birth      = serializers.DateField(required=False, allow_null=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email já cadastrado.")
        return value

    def create(self, validated_data):
        birth = validated_data.pop('birth', None)
        user  = User.objects.create_user(
            username   = validated_data['email'],
            email      = validated_data['email'],
            password   = validated_data['password'],
            first_name = validated_data['first_name'],
            last_name  = validated_data['last_name'],
        )
        if birth:
            user.person.birth = birth
            user.person.save()
        return user


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data['email']
        password = data['password']
        
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email ou senha incorretos.")
        
        user = authenticate(username=user_obj.username, password=password)
        if not user:
            raise serializers.ValidationError("Email ou senha incorretos.")
        if not user.is_active:
            raise serializers.ValidationError("Conta desativada.")
        
        data['user'] = user
        return data

class PersonSerializer(serializers.ModelSerializer):
    email      = serializers.EmailField(source='user.email',       read_only=True)
    first_name = serializers.CharField(source='user.first_name',   read_only=True)
    last_name  = serializers.CharField(source='user.last_name',    read_only=True)

    class Meta:
        model  = Person
        fields = ['person_id', 'email', 'first_name', 'last_name', 'birth', 'google_id']