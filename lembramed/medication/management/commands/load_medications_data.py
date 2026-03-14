import json,os
from django.core.management.base import BaseCommand
from medication.models import Medication

# python manage.py load_medications_data

# "columns": [
#         "TIPO_PRODUTO", 0
#         "NOME_PRODUTO", 1
#         "DATA_FINALIZACAO_PROCESSO", 2
#         "CATEGORIA_REGULATORIA", 3
#         "NUMERO_REGISTRO_PRODUTO", 4
#         "DATA_VENCIMENTO_REGISTRO", 5
#         "NUMERO_PROCESSO", 6
#         "CLASSE_TERAPEUTICA", 7
#         "EMPRESA_DETENTORA_REGISTRO", 8
#         "SITUACAO_REGISTRO", 9
#         "PRINCIPIO_ATIVO" 10
# ],
       
class Command(BaseCommand):
    help = "Load pre defined medications data from database"
    def handle(self, *args, **options):
        # file_path = "/home/yanetti/Desktop/extensao/server-medications/lembramed/api/src/anvisa_data/Medicamentos_teste.json"
        file_path = "/home/yanetti/Desktop/extensao/server-medications/lembramed/api/src/anvisa_data/Medicamentos_teste.json"
        with open (file_path, "r") as f:
            json_data = json.load(f)
            medications_list = json_data.get("data", [])
            for elemento in medications_list:
                if elemento[0] == 'MEDICAMENTO' and elemento[9] == 'VÁLIDO':
                    name = elemento[1]
                    medication_id = int(elemento[4])
                    empresa = elemento[8]
                    principio_ativo = elemento[10]
                    classe_terapeutica = elemento[7]
                    Medication.objects.update_or_create(
                        medication_id = medication_id,
                        defaults = {
                            'person_id':None,
                            'name': name,
                            'dosage': None,
                            'time': None,
                            'begin': None,
                            'end': None,
                            'days': None,
                            'formato': None,
                            'quantity': None,
                            'empresa': empresa,
                            'principio_ativo': principio_ativo,
                            'classe_terapeutica': classe_terapeutica,
                        }
                    )
            self.stdout.write(self.style.SUCCESS("Medication data successfully loaded."))

