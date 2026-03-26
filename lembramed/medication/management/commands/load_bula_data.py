import json,os
from django.core.management.base import BaseCommand
from medication.models import Bula_data 

# python manage.py load_bula_data (run command)

# update_or_create is slow with a large amount of items, use bulk_create instead afterwards

class Command(BaseCommand):
    help="Load pre defined bula data from database"
    def handle(self, *args, **options):
        # file_path = "lembramed/api/src/anvisa_data/Titulos_teste.json"
        # file_path = "../../../api/src/anvisa_data/Titulos_teste.json"
        # Base_dir = os. path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # caminho = os.path.join(Base_dir, "api","src","anvisa_data", "Titulos_teste.json")
        # file_path = "/home/user/Desktop/extensao/server-medications/lembramed/api/src/anvisa_data/Titulos_teste.json"
        file_path = "/home/yanetti/Desktop/extensao/server-medications/lembramed/api/src/anvisa_data/Titulos_teste.json"
        with open(file_path, 'r') as f:
            data = json.load(f)
            for key,var in data.items(): # key = register num, var = list of dicts (titulo:conteudo)
                indicacoes_para_uso = ""
                funcionamento_medicamento = ""
                quando_nao_usar = ""
                conhecimento_previo_necessario = ""
                como_usar_medicamento = ""
                esqueceu_medicamento = ""
                efeitos_colaterais = ""
                quantidade_a_mais = ""
                como_guardar_medicamento = ""
                for pares in var:
                    titulo = pares['titulo']
                    conteudo = pares['conteudo']
                    if titulo.startswith("PARA QUE ESTE MEDICAMENTO"):
                        indicacoes_para_uso = conteudo
                    elif titulo.startswith("COMO ESTE MEDICAMENTO FUNCIONA"):
                        funcionamento_medicamento = conteudo
                    elif titulo.startswith("QUANDO NÃO DEVO USAR ESTE MEDICAMENTO"):
                        quando_nao_usar = conteudo
                    elif titulo.startswith("O QUE DEVO SABER ANTES DE USAR"):
                        conhecimento_previo_necessario = conteudo
                    elif titulo.startswith("COMO DEVO USAR"):
                        como_usar_medicamento = conteudo
                    elif titulo.startswith("O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR"):
                        esqueceu_medicamento = conteudo
                    elif titulo.startswith("QUAIS OS MALES"):
                        efeitos_colaterais = conteudo
                    elif titulo.startswith("O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR"):
                        quantidade_a_mais = conteudo
                    elif titulo.startswith("ONDE COMO E POR QUANTO TEMPO POSSO GUARDAR"):
                        como_guardar_medicamento = conteudo
                # default deve ser tudo = "" (string vazia)
                Bula_data.objects.update_or_create(
                    register_Num = key,
                    defaults = {
                        'indicacoes_para_uso': indicacoes_para_uso,
                        'funcionamento_medicamento': funcionamento_medicamento,
                        'quando_nao_usar': quando_nao_usar,
                        'conhecimento_previo_necessario': conhecimento_previo_necessario,
                        'como_usar_medicamento': como_usar_medicamento,
                        'esqueceu_medicamento': esqueceu_medicamento,
                        'efeitos_colaterais': efeitos_colaterais,
                        'quantidade_a_mais': quantidade_a_mais,
                        'como_guardar_medicamento': como_guardar_medicamento,
                    }
                )
        self.stdout.write(self.style.SUCCESS("Bula data successfully loaded."))

