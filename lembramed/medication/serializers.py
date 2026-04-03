from rest_framework import serializers
from .models import Medication, Take, TakeRecord, Medication_Name, Active_Ingredient, ingredient_Interaction, Therapeutic_Class, Brand, Dosage, Company

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


class Medication_Name_Serializer(serializers.ModelSerializer):
      class Meta:
        model = Medication_Name
        fields = '__all__'

class Active_Ingredient_Serializer(serializers.ModelSerializer):
      class Meta:
        model = Active_Ingredient
        fields = '__all__'

class ingredient_Interaction_Serializer(serializers.ModelSerializer):
      class Meta:
        model = ingredient_Interaction
        fields = '__all__'


class Therapeutic_Class_Serializer(serializers.ModelSerializer):
      class Meta:
        model = Therapeutic_Class
        fields = '__all__'

class Brand_Serializer(serializers.ModelSerializer):
      class Meta:
        model = Brand
        fields = '__all__'

class Dosage_Serializer(serializers.ModelSerializer):
      class Meta:
        model = Dosage
        fields = '__all__'

class Company_Serializer(serializers.ModelSerializer):
      class Meta:
        model = Company
        fields = '__all__'
