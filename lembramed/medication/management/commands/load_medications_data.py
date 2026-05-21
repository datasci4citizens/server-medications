import json, os
from django.core.management.base import BaseCommand
from medication.models import (
    Medication, Medication_Name, Company,
   Active_Ingredient, Therapeutic_Class
)

class Command(BaseCommand):
    help = "Load pre defined medications data from database"

    def handle(self, *args, **options):
        BASE = "/server-medications/lembramed/api/src/anvisa_data"

        self.stdout.write("Carregando anvisa_data.json...")
        anvisa = {}
        with open(os.path.join(BASE, "anvisa_data.json"), "r") as f:
            json_data = json.load(f)
        for element in json_data.get("data", []):
            if element[0] == "MEDICAMENTO" and element[9] == "VÁLIDO":
                med_id = int(element[4])
                anvisa[med_id] = {
                    "name":               element[1],
                    "company":            element[8],
                    "active_ingridient":  element[10],
                    "therapeutic_class":  element[7],
                }
        self.stdout.write(f"  {len(anvisa)} medicamentos válidos.")

        self.stdout.write("Carregando bulas...")
        leaflets = {}
        for i in range(5):
            path = os.path.join(BASE, f"Bulario_medicamentos_iniciais{i}.json")
            if not os.path.exists(path):
                self.stdout.write(self.style.WARNING(f"  Não encontrado: {path}"))
                continue
            with open(path, "r") as f:
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
                leaflets[med_id] = camps
            self.stdout.write(f"  Bulario{i}: {len(data)} bulas")
        self.stdout.write(f"  Total bulas: {len(leaflets)}")

        self.stdout.write("Populando banco...")
        created = updated = no_leaflet = 0
        for med_id, info in anvisa.items():
            leaflet = leaflets.get(med_id, {})
            if not leaflet:
                no_leaflet += 1
            med, created = Medication.objects.update_or_create(
                medication_id=med_id,
                defaults={**info, **leaflet},
            )

            Medication_Name.objects.get_or_create(
                medication_id=med,
                name=info["name"]
            )

            Company.objects.get_or_create(
                medication_id=med,
                company=info["company"]
            )

            for principle in info["active_ingridient"].split("+"):
                principle =principle.strip()
                if principle:
                    Active_Ingredient.objecst.get_or_create(
                        medication_id=med,
                        active_ingredient=principle
                    )

            Therapeutic_Class.objects.get_or_create(
                medication_id=med,
                therapeutic_class=info["therapeutic_class"]
            )

            if created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Concluído: {created} criados, {updated} atualizados, {no_leaflet} sem bula."
        ))