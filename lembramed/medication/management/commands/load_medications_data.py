import json, os
from django.core.management.base import BaseCommand
from medication.models import Medication, Medication_Name, Company, Active_Ingredient, Therapeutic_Class
from pathlib import Path

class Command(BaseCommand):
    help = "Load pre defined medications data from database"

    def handle(self, *args, **options):
        cur = Path(__file__).resolve()
        root = cur.parent.parent.parent.parent.parent
        BASE = f"{root}/lembramed/api/src/anvisa_data/"
        anvisa = {}
        with open(os.path.join(BASE,"anvisa_data.json"), "r",encoding="utf-8") as f:
            json_data = json.load(f)
        for element in json_data.get("data", []):
            if element[0] == "MEDICAMENTO" and element[9] == "VÁLIDO":
                med_id = int(element[4])
                anvisa[med_id] = {
                    "name":               element[1],
                    "empresa":            element[8],
                    "principio_ativo":    element[10],
                    "classe_terapeutica": element[7],
                }
        self.stdout.write(f"{len(anvisa)} medicamentos válidos.")

        self.stdout.write("Carregando bulas...")
        leaflet = {}
        for i in range(5):
            path = os.path.join(BASE, f"Bulario_medicamentos_iniciais{i}.json")
            if not os.path.exists(path):
                self.stdout.write(self.style.WARNING(f"Não encontrado: {path}"))
                continue
            with open(path, "r",encoding="utf-8") as f:
                data = json.load(f)
            for key, var in data.items():
                med_id = int(key)
                camps = {
                    "indicacoes_para_uso": "",
                    "funcionamento_medicamento": "",
                    "quando_nao_usar": "",
                    "conhecimento_previo_necessario": "",
                    "como_usar_medicamento": "",
                    "esqueceu_medicamento": "",
                    "efeitos_colaterais": "",
                    "quantidade_a_mais": "",
                    "como_guardar_medicamento": "",
                }
                for pairs in var:
                    title  = pairs["titulo"]
                    content = pairs["conteudo"]
                    if title.startswith("PARA QUE ESTE MEDICAMENTO"):
                        camps["indicacoes_para_uso"] = content
                    elif title.startswith("COMO ESTE MEDICAMENTO FUNCIONA"):
                        camps["funcionamento_medicamento"] = content
                    elif title.startswith("QUANDO NÃO DEVO USAR"):
                        camps["quando_nao_usar"] = content
                    elif title.startswith("O QUE DEVO SABER ANTES DE USAR"):
                        camps["conhecimento_previo_necessario"] = content
                    elif title.startswith("COMO DEVO USAR"):
                        camps["como_usar_medicamento"] = content
                    elif title.startswith("O QUE DEVO FAZER QUANDO EU ME ESQUECER"):
                        camps["esqueceu_medicamento"] = content
                    elif title.startswith("QUAIS OS MALES"):
                        camps["efeitos_colaterais"] = content
                    elif title.startswith("O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR"):
                        camps["quantidade_a_mais"] = content
                    elif title.startswith("ONDE COMO E POR QUANTO TEMPO POSSO GUARDAR"):
                        camps["como_guardar_medicamento"] = content
                leaflet[med_id] = camps
            self.stdout.write(f"  Bulario{i}: {len(data)} bulas")
        self.stdout.write(f"  Total bulas: {len(leaflet)}")
        def clean_text(text):
            if not text:
                return ""
            return str(text).replace('\x00', '')
        self.stdout.write("Populando banco...")
        created_med = updated_med = no_leaflet = 0
        for med_id, info in anvisa.items():
            # print(info)
            # print(clean_text(info.get("name","")))
            # print(clean_text(info.get("active_ingredient")))
            # print(info.get("therapeutic_class",""))
            # print(info.get("company",""))
            med_leaflet = leaflet.get(med_id, {})
            if not med_leaflet:
                no_leaflet += 1
            medication_object, created = Medication.objects.update_or_create( # Medication == med_leaflet
                medication_id = med_id,
                defaults = {
                    "indicacoes_para_uso":clean_text(med_leaflet.get("indicacoes_para_uso", "")),
                    "funcionamento_medicamento":clean_text(med_leaflet.get("funcionamento_medicamento", "")),
                    "quando_nao_usar":clean_text(med_leaflet.get("quando_nao_usar", "")),
                    "conhecimento_previo_necessario":clean_text(med_leaflet.get("conhecimento_previo_necessario", "")),
                    "como_usar_medicamento":clean_text(med_leaflet.get("como_usar_medicamento", "")),
                    "esqueceu_medicamento":clean_text(med_leaflet.get("esqueceu_medicamento", "")),
                    "efeitos_colaterais":clean_text(med_leaflet.get("efeitos_colaterais", "")),
                    "quantidade_a_mais":clean_text(med_leaflet.get("quantidade_a_mais", "")),
                    "como_guardar_medicamento":clean_text(med_leaflet.get("como_guardar_medicamento", ""))
                }
            )
            if created:
                created_med += 1
            else:
                updated_med += 1
            # anvisa[med_id] = {
            #                     "name":               element[1],
            #                     "empresa":            element[8],
            #                     "principio_ativo":    element[10],
            #                     "classe_terapeutica": element[7],
            #                 }
            #  company, name, active_ingredients, classe_terapeutica
            _,n = Medication_Name.objects.update_or_create(
                medication_id = medication_object,
                defaults = {"name":clean_text(info.get("name",""))}
            )
            _,ai = Active_Ingredient.objects.update_or_create(
                medication_id = medication_object,
                defaults = {'active_ingredient':clean_text(info.get('principio_ativo',""))}
            )
            _,tc = Therapeutic_Class.objects.update_or_create(
                medication_id = medication_object,
                defaults = { 'therapeutic_class':clean_text(info.get('classe_terapeutica',""))}
            )
            _,c = Company.objects.update_or_create(
                medication_id = medication_object,
                defaults = {'company':clean_text(info.get('empresa',""))}
            )
        self.stdout.write(self.style.SUCCESS(
            f"Concluído: {created_med} created_med, {updated_med} updated_med, {no_leaflet} sem bula."
        ))