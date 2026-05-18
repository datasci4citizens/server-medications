from rest_framework import serializers
from ..models import (
    Medication, Medication_Name, Active_Ingredient,
    Brand, Dosage, Formato, Therapeutic_Class, Category,
    Company
)
from .leaflet_serializer import LeafletSerializer

class MedicationSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(many=True)
    active_ingredient = serializers.StringRelatedField(source='ingredient', many=True)
    therapeutic_class = serializers.StringRelatedField(many=True)
    category = serializers.StringRelatedField(many=True)
    brand = serializers.StringRelatedField(many=True)
    dosage = serializers.StringRelatedField(many=True)
    company = serializers.StringRelatedField(many=True)
    formato = serializers.StringRelatedField(many = True)
    leaflet = LeafletSerializer()
    class Meta:
        model = Medication
        fields = ["medication_id","process_num","name","active_ingredient",
        "therapeutic_class","category","brand","dosage","company",
        "formato","leaflet"]

class MedicationNameSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Medication_Name
        fields = ['name']
        read_only_fields = ['medication_id']

class ActiveIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Active_Ingredient
        fields = ['active_ingredient']
        read_only_fields = ['medication_id']

class TherapeuticClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Therapeutic_Class
        fields = ['therapeutic_class']
        read_only_fields = ['medication_id']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category']
        read_only_fields = ['medication_id']
    
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['brand']
        read_only_fields = ['medication_id']

class DosageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dosage
        fields = ['dosage']
        read_only_fields = ['medication_id']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['company']
        read_only_fields = ['medication_id']

class FormatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formato
        fields = ['formato']
        read_only_fields = ['medication_id']