from rest_framework import serializers
from .models import Medication, Take, TakeRecord

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'
        # fields = ["medication_id", "person_id","name", "dosage", "time", "begin", "end", "quantity", "formato"]

class TakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Take
        fields = '__all__'

class TakeRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TakeRecord
        fields = '__all__'
