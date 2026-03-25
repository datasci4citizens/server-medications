from rest_framework import serializers
from .models import Medication, Bula_data

# nome da marca, OK?
# comprimido/dosagem, OK
# forma de medicacao (pilula...), ok
# horario, OK
# quantidade, ok
# lembrete de repor estoque (lembrete), !!!!!!!!!
# inicio e final de tratamento (opcional) OK

class MedicationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Medication
        # fields = '__all__'
        fields = ["medication_id", "person_id","name", "dosage", "time", "begin", "end", "quantity", "formato"]

class BulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bula_data
        fields = '__all__'