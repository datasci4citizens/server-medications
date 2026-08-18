from django.contrib.auth.models import User
from rest_framework import serializers
from medication.models.medication_model import Medication

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'password',
#                   'first_name', 'last_name']
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }