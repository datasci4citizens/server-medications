from django.contrib import admin
from .models import Medication, Take, Medication_Name, Active_Ingredient,ingredient_Interaction, Therapeutic_Class, Brand, Dosage, Company
admin.site.register(Medication)
admin.site.register(Medication_Name)
admin.site.register(Take)
admin.site.register(Active_Ingredient)
admin.site.register(ingredient_Interaction)
admin.site.register(Therapeutic_Class)
admin.site.register(Brand)
admin.site.register(Dosage)
admin.site.register(Company)