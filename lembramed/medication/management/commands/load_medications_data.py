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
        for elemento in json_data.get("data", []):
            if elemento[0] == "MEDICAMENTO" and elemento[9] == "VÁLIDO":
                med_id = int(elemento[4])
                anvisa[med_id] = {
                    "name":               elemento[1],
                    "empresa":            elemento[8],
                    "principio_ativo":    elemento[10],
                    "classe_terapeutica": elemento[7],
                }
        self.stdout.write(f"{len(anvisa)} medicamentos válidos.")

        self.stdout.write("Carregando bulas...")
        bulas = {}
        for i in range(5):
            path = os.path.join(BASE, f"Bulario_medicamentos_iniciais{i}.json")
            if not os.path.exists(path):
                self.stdout.write(self.style.WARNING(f"Não encontrado: {path}"))
                continue
            with open(path, "r",encoding="utf-8") as f:
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
        def clean_text(text):
            if not text:
                return ""
            return str(text).replace('\x00', '')
        self.stdout.write("Populando banco...")
        criados = atualizados = sem_bula = 0
        for med_id, info in anvisa.items():
            # print(info)
            # print(clean_text(info.get("name","")))
            # print(clean_text(info.get("active_ingredient")))
            # print(info.get("therapeutic_class",""))
            # print(info.get("company",""))
            bula = bulas.get(med_id, {})
            if not bula:
                sem_bula += 1
            medication_object, created = Medication.objects.update_or_create( # Medication == Bula
                medication_id = med_id,
                defaults = {
                    "indicacoes_para_uso":clean_text(bula.get("indicacoes_para_uso", "")),
                    "funcionamento_medicamento":clean_text(bula.get("funcionamento_medicamento", "")),
                    "quando_nao_usar":clean_text(bula.get("quando_nao_usar", "")),
                    "conhecimento_previo_necessario":clean_text(bula.get("conhecimento_previo_necessario", "")),
                    "como_usar_medicamento":clean_text(bula.get("como_usar_medicamento", "")),
                    "esqueceu_medicamento":clean_text(bula.get("esqueceu_medicamento", "")),
                    "efeitos_colaterais":clean_text(bula.get("efeitos_colaterais", "")),
                    "quantidade_a_mais":clean_text(bula.get("quantidade_a_mais", "")),
                    "como_guardar_medicamento":clean_text(bula.get("como_guardar_medicamento", ""))
                }
            )
            if created:
                criados += 1
            else:
                atualizados += 1
            # anvisa[med_id] = {
            #                     "name":               elemento[1],
            #                     "empresa":            elemento[8],
            #                     "principio_ativo":    elemento[10],
            #                     "classe_terapeutica": elemento[7],
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
            f"Concluído: {criados} criados, {atualizados} atualizados, {sem_bula} sem bula."
        ))