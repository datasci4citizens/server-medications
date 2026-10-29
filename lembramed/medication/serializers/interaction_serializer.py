from rest_framework import serializers
from ..models import ingredient_Interaction

class ingredientInteractionSerializer(serializers.ModelField):
    class Meta:
        model = ingredient_Interaction
        fields = '__all__'