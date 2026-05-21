from rest_framework import serializers
from .models import Medication, Take, TakeRecord, Medication_Name, Active_Ingredient, ingredient_Interaction, Therapeutic_Class, Brand, Dosage, Company

class MedicationSerializer(serializers.ModelSerializer):
    #read only
    indicacoes_para_uso = serializers.ReadOnlyField()
    funcionamento_medicamento = serializers.ReadOnlyField()
    quando_nao_usar = serializers.ReadOnlyField()
    conhecimento_previo_necessario = serializers.ReadOnlyField()
    como_guardar_medicamento = serializers.ReadOnlyField()
    como_usar_medicamento = serializers.ReadOnlyField()
    esqueceu_medicamento = serializers.ReadOnlyField()
    efeitos_colaterais = serializers.ReadOnlyField()
    quantidade_a_mais = serializers.ReadOnlyField()
    
    class Meta:
        model = Medication
        fields = '__all__'
        read_only_fields = [
            'medication_id', 
            'indicacoes_para_uso',
            'funcionamento_medicamento',
            'quando_nao_usar',
            'conhecimento_previo_necessario',
            'como_guardar_medicamento',
            'como_usar_medicamento',
            'esqueceu_medicamento',
            'efeitos_colaterais',
            'quantidade_a_mais'
        ]

class TakeSerializer(serializers.ModelSerializer):
    medication_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Take
        fields = ['taken_id', 'person_id', 'medication_id', 'medication_name', 'priority', 'quantity']
        read_only_fields = ['taken_id', 'person_id']
    
    def get_medication_name(self, obj):
        """Retorna o nome do medicamento"""
        name = obj.medication_id.name.first()
        return name.name if name else 'Medicamento sem nome'

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
