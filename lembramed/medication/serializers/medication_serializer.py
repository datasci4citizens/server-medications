from rest_framework import serializers
from ..models import (
    Medication, Medication_Name, Active_Ingredient,
    Brand, Therapeutic_Class, Category, Company
)

class MedicationNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication_Name
        fields = ['name']


class ActiveIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Active_Ingredient
        fields = ['active_ingredient']

    def to_internal_value(self, data):
        if isinstance(data, str):
            return {'active_ingredient': data}
        return super().to_internal_value(data)

class MedicationSerializer(serializers.ModelSerializer):
    leaflet = serializers.SerializerMethodField()

    def get_leaflet(self, obj):
        from .leaflet_serializer import LeafletSerializer
        return LeafletSerializer(obj.leaflet).data if hasattr(obj, "leaflet") else None

    name = serializers.CharField(required=False, allow_null=True)
    category = serializers.CharField(required=False, allow_null=True)
    company = serializers.CharField(required=False, allow_null=True)
    brand = serializers.CharField(required=False, allow_null=True)
    therapeutic_class = serializers.CharField(required=False, allow_null=True)
    active_ingredients = ActiveIngredientSerializer(many=True, required=False)

    class Meta:
        model = Medication
        fields = [
            "medication_id", "process_num", "name",
            "active_ingredients", "therapeutic_class",
            "category", "brand", "company", "leaflet",
        ]
    
    def _resolve_relation(self, model_class, field_name, value):
        if not value:
            return None
        
        text = value.get(field_name) if isinstance(value, dict) else str(value).strip()
        obj, _ = model_class.objects.get_or_create(**{field_name: text})

        return obj
    
    def create(self, validated_data):
        active_ingredients_data = validated_data.pop('active_ingredients', [])
        
        name_val = validated_data.pop('name', None)
        category_val = validated_data.pop('category', None)
        company_val = validated_data.pop('company', None)
        brand_val = validated_data.pop('brand', None)
        tc_val = validated_data.pop('therapeutic_class', None)
        medication = Medication.objects.create(
            name=self._resolve_relation(Medication_Name, 'name', name_val),
            category=self._resolve_relation(Category, 'category', category_val),
            company=self._resolve_relation(Company, 'company', company_val),
            brand=self._resolve_relation(Brand, 'brand', brand_val),
            therapeutic_class=self._resolve_relation(Therapeutic_Class, 'therapeutic_class', tc_val),
            **validated_data
        )
        for ai_item in active_ingredients_data:
            ai_name = ai_item.get('active_ingredient') if isinstance(ai_item, dict) else str(ai_item)
            if ai_name:
                ai_obj, _ = Active_Ingredient.objects.get_or_create(active_ingredient=ai_name.strip())
                medication.active_ingredients.add(ai_obj)
        return medication
    
    def update(self, instance, validated_data):
        active_ingredients_data = validated_data.pop('active_ingredients', None)
        if 'name' in validated_data:
            instance.name = self._resolve_relation(Medication_Name, 'name', validated_data.pop('name'))
        if 'category' in validated_data:
            instance.category = self._resolve_relation(Category, 'category', validated_data.pop('category'))
        if 'company' in validated_data:
            instance.company = self._resolve_relation(Company, 'company', validated_data.pop('company'))
        if 'brand' in validated_data:
            instance.brand = self._resolve_relation(Brand, 'brand', validated_data.pop('brand'))
        if 'therapeutic_class' in validated_data:
            instance.therapeutic_class = self._resolve_relation(Therapeutic_Class, 'therapeutic_class', validated_data.pop('therapeutic_class'))
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if active_ingredients_data is not None:
            instance.active_ingredients.clear()
            for ai_item in active_ingredients_data:
                ai_name = ai_item.get('active_ingredient') if isinstance(ai_item, dict) else str(ai_item)
                if ai_name:
                    ai_obj, _ = Active_Ingredient.objects.get_or_create(active_ingredient=ai_name.strip())
                    instance.active_ingredients.add(ai_obj)
        return instance
    
    def to_representation(self, instance):
        """Format the output string representations for GET responses."""

        data = super().to_representation(instance)
        data['name'] = instance.name.name if instance.name else None
        data['category'] = instance.category.category if instance.category else None
        data['company'] = instance.company.company if instance.company else None
        data['brand'] = instance.brand.brand if instance.brand else None
        data['therapeutic_class'] = instance.therapeutic_class.therapeutic_class if instance.therapeutic_class else None
        
        return data

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


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['company']

