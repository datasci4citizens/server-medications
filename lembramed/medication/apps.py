from django.apps import AppConfig
from django.core.management import call_command

class MedicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medication'
    def ready(self):
        call_command("load_bula_data")
        call_command("load_medications_data")
