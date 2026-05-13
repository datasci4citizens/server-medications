from rest_framework import serializers
from .models import Leaflet, Take, TakeRecord

class LeafletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaflet
        fields = '__all__'

class TakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Take
        fields = '__all__'

class TakeRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TakeRecord
        fields = '__all__'
