from django.contrib import admin
from .models import Medication, Take, Medication_Name, Active_Ingredient, ingredient_Interaction, Therapeutic_Class, Brand, Dosage, Company

class MedicationAdmin(admin.ModelAdmin):
    # protec leaflet camps of being manualy edited
    readonly_fields = [
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
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('medication_id',),
            'description': 'ID do medicamento (carregado da ANVISA)'
        }),
        ('Informações do Bulário', {
            'fields': (
                'indicacoes_para_uso',
                'funcionamento_medicamento',
                'quando_nao_usar',
                'conhecimento_previo_necessario',
                'como_guardar_medicamento',
                'como_usar_medicamento',
                'esqueceu_medicamento',
                'efeitos_colaterais',
                'quantidade_a_mais'
            ),
            'description': 'Campos carregados automaticamente dos 5 bulários. Somente leitura.',
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Desabilita adição manual de medicamentos"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Desabilita deleção de medicamentos"""
        return False

class TakeAdmin(admin.ModelAdmin):
    """Admin para medicamentos que a pessoa está tomando"""
    list_display = ('taken_id', 'person_id', 'medication_id','quantity')
    list_filter = ('person_id',)
    search_fields = ('person_id__user__email', 'medication_id__medication_id')
    readonly_fields = ('taken_id',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('taken_id', 'person_id', 'medication_id')
        }),
        ('Configurações', {
            'fields': ('quantity',)
        }),
    )

admin.site.register(Medication, MedicationAdmin)
admin.site.register(Medication_Name)
admin.site.register(Take, TakeAdmin)
admin.site.register(Active_Ingredient)
admin.site.register(ingredient_Interaction)
admin.site.register(Therapeutic_Class)
admin.site.register(Brand)
admin.site.register(Dosage)
admin.site.register(Company)