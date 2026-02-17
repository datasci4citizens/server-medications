from rest_framework import serializers
from .models import Medication

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
        fields = ["medication_id", "person_id","name", "dosage", "time", "begin", "end", "quantity", "format"]