from rest_framework import serializers
from ..models import (
    Medication, Medication_Name, Active_Ingredient,
    Brand, Dosage, Formato, Therapeutic_Class, Category,
    Company
)
from .leaflet_serializer import LeafletSerializer

class MedicationSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField()
    active_ingredients = serializers.StringRelatedField(many=True)
    therapeutic_class = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()
    dosage = serializers.StringRelatedField()
    company = serializers.StringRelatedField()
    formato = serializers.StringRelatedField()
    leaflet = LeafletSerializer()
    class Meta:
        model = Medication
        fields = ["medication_id","process_num","name","active_ingredients",
        "therapeutic_class","category","brand","dosage","company",
        "formato","leaflet"]


class MedicationNameSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Medication_Name
        fields = ['name']

class ActiveIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Active_Ingredient
        fields = ['active_ingredient']

class TherapeuticClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Therapeutic_Class
        fields = ['therapeutic_class']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category']
    
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['brand']

class DosageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dosage
        fields = ['dosage']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['company']

class FormatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formato
        fields = ['formato']