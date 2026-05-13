from django.contrib import admin
from .models import Leaflet, Take, Medication_Name, Formato, Active_Ingredient,ingredient_Interaction, Therapeutic_Class, Brand, Dosage, Company, Category
admin.site.register(Leaflet)
admin.site.register(Medication_Name)
admin.site.register(Take)
admin.site.register(Active_Ingredient)
admin.site.register(ingredient_Interaction)
admin.site.register(Therapeutic_Class)
admin.site.register(Brand)
admin.site.register(Dosage)
admin.site.register(Company)
admin.site.register(Category)
admin.site.register(Formato)