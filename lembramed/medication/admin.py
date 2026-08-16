from django.contrib import admin
from .models import (Leaflet, Take, TakeRecord, Medication_Name,
Formato, Active_Ingredient,ingredient_Interaction, Therapeutic_Class,
Brand, Presentation, Company, Category, Medication, TimeStampedModel)

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    readonly_fields = [ 'created_at', 'updated_at']
    search_fields = [ 'medication_id', 'process_num']
    list_filter = [ 'medication_id', 'process_num']
    list_display = ['medication_id', 'process_num', 'created_at']
    autocomplete_fields = ['category', 'company', 'brand', 'name', 'therapeutic_class', 'presentation', 'active_ingredients']

@admin.register(Leaflet)
class LeafletAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['medication_id']
    list_filter = ['medication_id']
    list_display = ['medication_id', 'created_at']

@admin.register(Take)
class TakeAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['person_id', 'medication_id', 'taken_id']
    list_filter = [ 'priority', 'person_id', 'medication_id']
    list_display = ['medication_id', 'created_at']

@admin.register(TakeRecord)
class TakeRecordAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = [ 'taken_id', 'begin', 'end', 'state']
    list_filter = [ 'begin', 'end', 'days', 'cycle_type', 'take_at', 'take_cycle', 'state']
    list_display = ['taken_id', 'created_at']

@admin.register(Medication_Name)
class MedicationNameAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['name']
    list_display = ['name', 'created_at']

@admin.register(Active_Ingredient)
class ActiveIngredientAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['active_ingredient']
    list_filter = ['active_ingredient']
    list_display = ['active_ingredient', 'created_at']

@admin.register(ingredient_Interaction)
class IngredientInteractionAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['active_ingredient1' , 'active_ingredient2', 'severity']
    list_filter = ['severity']
    list_display = ['active_ingredient1','active_ingredient2']

@admin.register(Therapeutic_Class)
class TherapeuticClassAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['therapeutic_class']
    list_filter = ['therapeutic_class']
    list_display = ['therapeutic_class', 'created_at']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['brand']
    list_filter =  ['brand']
    list_display = ['brand', 'created_at']

@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['register_num']
    list_filter = ['register_num']
    list_display = ['register_num', 'created_at']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['company']
    list_filter = ['company']
    list_display = ['company', 'created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['category']
    list_filter = ['category']
    list_display = ['category', 'created_at']

@admin.register(Formato)
class FormatoAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['formato']
    list_filter = ['formato']
    list_display = ['formato', 'created_at']