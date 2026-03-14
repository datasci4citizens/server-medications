import json,os
from django.core.management.base import BaseCommand
from medication.models import Medication

# editar o inii.py e o app.py do medication

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

# django.core.exceptions.FieldError: Cannot resolve keyword 'medication_id', 'DAYS_OF_WEEK
# into field. Choices are: begin, classe_terapeutica, days, dosage, empresa, end, 
# format, id, name, person_id, person_id_id, principio_ativo, quantity, time

class Command(BaseCommand):
    help = "Load pre defined medications data from database"
    def handle(self, *args, **options):
        #file_path = "/home/yanetti/Desktop/extensao/server-medications/lembramed/api/src/anvisa_data/Medicamentos_teste.json"
        Base_dir = os. path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho = os.path.join(Base_dir, "api","src","anvisa_data", "Medicamentos_teste.json")
        with open ((caminho), "r") as f:
            data = json.load(f)
            for data_colums,lista in data.items():
                # medication_id = ''
                person_id = '1' #FALTA
                # DAYS_OF_WEEK = '__all__' #FALTA
                # === ! === ! === ! === !
                name = ''
                dosage = '' #FALTA
                time = '' #FALTA
                begin = '' #FALTA
                end = '' #FALTA
                days = '' #FALTA
                formato = '' #FALTA
                quantity = '' #FALTA
                empresa = ''
                principio_ativo = ''
                classe_terapeutica = ''
                if data_colums == "data":
                    for elemento in lista:
                        # print(f"{elemento}\n\n")
                        if elemento[0] == 'MEDICAMENTO' and elemento[9] == 'VÁLIDO':
                            name += elemento[1]
                            # medication_id += str(int(elemento[4]))
                            empresa += elemento[8]
                            principio_ativo += elemento[10]
                            classe_terapeutica += elemento[7]
                Medication.objects.update_or_create(
                    # medication_id = medication_id,
                    person_id = person_id,
                    # DAYS_OF_WEEK = DAYS_OF_WEEK,
                    defaults = {
                        'name': name,
                        'dosage': dosage,
                        'time': time,
                        'begin': begin,
                        'end': end,
                        'days': days,
                        'format': formato,
                        'quantity': quantity,
                        'empresa': empresa,
                        'principio_ativo': principio_ativo,
                        'classe_terapeutica': classe_terapeutica,
                    }
                )
            self.stdout.write(self.style.SUCCESS("Medication data successfully loaded."))

