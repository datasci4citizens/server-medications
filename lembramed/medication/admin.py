from django.contrib import admin
from .models import (Leaflet, Take, TakeRecord, Medication_Name,
Formato, Active_Ingredient,ingredient_Interaction, Therapeutic_Class,
Brand, Dosage, Company, Category, Medication, TimeStampedModel)

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    readonly_fields = [ 'created_at', 'updated_at']
    search_fields = [ 'medication_id', 'process_num']
    list_filter = [ 'medication_id', 'process_num']

@admin.register(Leaflet)
class LeafletAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = [ 'medication_id']
    list_filter = [ 'medication_id']

@admin.register(Take)
class TakeAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = [ 'person_id', 'medication_id', 'taken_id']
    list_filter = [ 'priority', 'person_id', 'medication_id']

@admin.register(TakeRecord)
class TakeRecordAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = [ 'taken_id', 'begin', 'end', 'state']
    list_filter = [ 'begin', 'end', 'days', 'cycle_type', 'take_at', 'take_cycle', 'state']

@admin.register(Medication_Name)
class MedicationNameAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = [ 'medication_id', 'name']
    list_filter = ['medication_id']

# @admin.register(Active_Ingredient)
# class ActiveIngredientAdmin(admin.ModelAdmin):
#     readonly_fields = ['created_at', 'updated_at']
#     search_fields = [ 'medication_id', 'active_ingredient']
#     list_filter = [ 'medication_id', 'active_ingredient']

@admin.register(Active_Ingredient)
class ActiveIngredientAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['medication__medication_id', 'active_ingredient']
    list_display = ['active_ingredient', 'medication', 'created_at']
    list_filter = ['medication']

@admin.register(ingredient_Interaction)
class IngredientInteractionAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['active_ingredient1' , 'active_ingredient2', 'severity']
    list_filter = ['severity']

@admin.register(Therapeutic_Class)
class TherapeuticClassAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['medication_id', 'therapeutic_class']
    list_filter = [ 'medication_id', 'therapeutic_class']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['medication_id', 'brand']
    list_filter =  ['medication_id', 'brand']

@admin.register(Dosage)
class DosageAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['medication_id', 'dosage']
    list_filter = ['medication_id', 'dosage']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['medication_id', 'company']
    list_filter = ['medication_id', 'company']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['medication_id', 'category']
    list_filter = ['medication_id', 'category']

@admin.register(Formato)
class FormatoAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['medication_id', 'formato']
    list_filter = ['medication_id', 'formato']