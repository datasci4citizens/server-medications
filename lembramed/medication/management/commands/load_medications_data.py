import json, os
from django.core.management.base import BaseCommand
from medication.models import Medication

class Command(BaseCommand):
    help = "Load pre defined medications data from database"

    def handle(self, *args, **options):
        BASE = "/home/yanetti/Desktop/extensao/server-medications/lembramed/api/src/anvisa_data"

        # ── 1. Carrega dados da ANVISA em memória ─────────────────────────────
        self.stdout.write("Carregando anvisa_data.json...")
        anvisa = {}  # medication_id → {name, empresa, principio_ativo, classe_terapeutica}
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

        # ── 2. Carrega bulas dos 3 arquivos em memória ────────────────────────
        self.stdout.write("Carregando bulas...")
        bulas = {}  # medication_id → {indicacoes_para_uso, ...}
        for i in range(3):
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
                bulas[med_id] = campos  # salva no dict, não bate no banco aqui
            self.stdout.write(f"  Bulario{i}: {len(data)} bulas")
        self.stdout.write(f"  Total bulas: {len(bulas)}")

        # ── 3. Uma única passagem no banco ────────────────────────────────────
        self.stdout.write("Populando banco...")
        criados = atualizados = sem_bula = 0
        for med_id, info in anvisa.items():
            bula = bulas.get(med_id, {})
            if not bula:
                sem_bula += 1
            _, created = Medication.objects.update_or_create(
                medication_id=med_id,
                defaults={**info, **bula},
            )
            if created:
                criados += 1
            else:
                atualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Concluído: {criados} criados, {atualizados} atualizados, {sem_bula} sem bula."
        ))