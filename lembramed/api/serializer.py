from rest_framework import serializers
from medication.serializers import MedicationSerializer, LeafletSerializer, AnvisaRegisterSerializer

class DrugSerializer(serializers.ModelSerializer):
    medication = MedicationSerializer()
    leaflet = LeafletSerializer()
    register = AnvisaRegisterSerializer()