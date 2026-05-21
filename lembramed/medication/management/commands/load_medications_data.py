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
        for elemento in json_data.get("data", []):
            if elemento[0] == "MEDICAMENTO" and elemento[9] == "VÁLIDO":
                med_id = int(elemento[4])
                anvisa[med_id] = {
                    "name":               elemento[1],
                    "empresa":            elemento[8],
                    "principio_ativo":    elemento[10],
                    "classe_terapeutica": elemento[7],
                }
        self.stdout.write(f"  {len(anvisa)} medicamentos válidos.")

        self.stdout.write("Carregando bulas...")
        bulas = {}
        for i in range(5):
            path = os.path.join(BASE, f"Bulario_medicamentos_iniciais{i}.json")
            if not os.path.exists(path):
                self.stdout.write(self.style.WARNING(f"  Não encontrado: {path}"))
                continue
            with open(path, "r") as f:
                data = json.load(f)
            for key, var in data.items():
                med_id = int(key)
                campos = {
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
                for pares in var:
                    titulo  = pares["titulo"]
                    conteudo = pares["conteudo"]
                    if titulo.startswith("PARA QUE ESTE MEDICAMENTO"):
                        campos["indicacoes_para_uso"] = conteudo
                    elif titulo.startswith("COMO ESTE MEDICAMENTO FUNCIONA"):
                        campos["funcionamento_medicamento"] = conteudo
                    elif titulo.startswith("QUANDO NÃO DEVO USAR"):
                        campos["quando_nao_usar"] = conteudo
                    elif titulo.startswith("O QUE DEVO SABER ANTES DE USAR"):
                        campos["conhecimento_previo_necessario"] = conteudo
                    elif titulo.startswith("COMO DEVO USAR"):
                        campos["como_usar_medicamento"] = conteudo
                    elif titulo.startswith("O QUE DEVO FAZER QUANDO EU ME ESQUECER"):
                        campos["esqueceu_medicamento"] = conteudo
                    elif titulo.startswith("QUAIS OS MALES"):
                        campos["efeitos_colaterais"] = conteudo
                    elif titulo.startswith("O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR"):
                        campos["quantidade_a_mais"] = conteudo
                    elif titulo.startswith("ONDE COMO E POR QUANTO TEMPO POSSO GUARDAR"):
                        campos["como_guardar_medicamento"] = conteudo
                bulas[med_id] = campos
            self.stdout.write(f"  Bulario{i}: {len(data)} bulas")
        self.stdout.write(f"  Total bulas: {len(bulas)}")

        self.stdout.write("Populando banco...")
        criados = atualizados = sem_bula = 0
        for med_id, info in anvisa.items():
            bula = bulas.get(med_id, {})
            if not bula:
                sem_bula += 1
            med, created = Medication.objects.update_or_create(
                medication_id=med_id,
                defaults={**info, **bula},
            )

            Medication_Name.objects.get_or_create(
                medication_id=med,
                name=info["name"]
            )

            Company.objects.get_or_create(
                medication_id=med,
                company=info["empresa"]
            )

            for principio in info["principio_ativo"].split("+"):
                principio =principio.strip()
                if principio:
                    Active_Ingredient.objecst.get_or_create(
                        medication_id=med,
                        active_ingredient=principio
                    )

            Therapeutic_Class.objects.get_or_create(
                medication_id=med,
                therapeutic_class=info["classe_terapeutica"]
            )

            if created:
                criados += 1
            else:
                atualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Concluído: {criados} criados, {atualizados} atualizados, {sem_bula} sem bula."
        ))