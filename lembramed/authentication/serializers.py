from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Person



class RegisterSerializer(serializers.Serializer):
    email      = serializers.EmailField()
    first_name = serializers.CharField()
    last_name  = serializers.CharField(required=False, allow_blank=True, default='')
    profile = serializers.JSONField(required=False, default=dict)
    password   = serializers.CharField(write_only=True, min_length=8)
    birth      = serializers.DateField(required=False, allow_null=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email já cadastrado.")
        return value

    def create(self, validated_data):
        profile = validated_data.pop('profile', {})
        birth = validated_data.pop('birth', None)
        user  = User.objects.create_user(
            username   = validated_data['email'],
            email      = validated_data['email'],
            password   = validated_data['password'],
            first_name = validated_data['first_name'],
            last_name  = validated_data['last_name'],
        )
        user.person.profile = profile
        user.person.save(update_fields=['profile'])
        if birth is not None:
            user.person.birth = birth
            user.person.save()
        return user


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get('email'), password=data.get('password'))
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
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)
    is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)

    class Meta:
        model  = Person
        fields = ['profile', 'person_id', 'email', 'first_name', 'last_name', 'birth', 'is_staff', 'is_superuser']