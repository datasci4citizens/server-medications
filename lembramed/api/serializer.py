from rest_framework import serializers
from .models import 
class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'
        # fields = ["medication_id", "person_id","name", "dosage", "time", "begin", "end", "quantity", "formato"]
