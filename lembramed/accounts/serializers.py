from rest_framework import serializers
from .models import New_Person

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = New_Person
        # fields = '__all__'
        fields = ["person_id", "name", "email", "password"]
