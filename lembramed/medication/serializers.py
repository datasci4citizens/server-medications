from rest_framework import serializers
from .models import Medication

# nome da marca, OK?
# comprimido/dosagem, OK
# forma de medicacao (pilula...), !!!!!!!!!
# horario, OK
# quantidade, !!!!!!!!!!
# lembrete de repor estoque (lembrete), !!!!!!!!!
# inicio e final de tratamento (opcional) OK

class MedicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Medication
        # fields = '__all__'
        fields = ["medication_id", "person_id","name", "dosage", "time", "begin", "end"]