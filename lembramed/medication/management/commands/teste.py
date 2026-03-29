import json
import os
from django.core.management.base import BaseCommand
from medication.models import Medication

BASE = "/home/yanetti/Desktop/extensao/server-medications/lembramed/api/src/anvisa_data/"

ANVISA_JSON   = os.path.join(BASE, "anvisa_data.json")
BULARIO_JSONS = [
    os.path.join(BASE, "Bulario_medicamentos_iniciais0.json"),
    os.path.join(BASE, "Bulario_medicamentos_iniciais1.json"),
    os.path.join(BASE, "Bulario_medicamentos_iniciais2.json"),
]


def _parse_bula(var: list) -> dict:
    """Recebe a lista de {titulo, conteudo} de um registro e retorna dict com os campos."""
    fields = {
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
    for par in var:
        titulo  = par.get("titulo", "")
        conteudo = par.get("conteudo", "")
        if titulo.startswith("PARA QUE ESTE MEDICAMENTO"):
            fields["indicacoes_para_uso"] = conteudo
        elif titulo.startswith("COMO ESTE MEDICAMENTO FUNCIONA"):
            fields["funcionamento_medicamento"] = conteudo
        elif titulo.startswith("QUANDO NÃO DEVO USAR"):
            fields["quando_nao_usar"] = conteudo
        elif titulo.startswith("O QUE DEVO SABER ANTES DE USAR"):
            fields["conhecimento_previo_necessario"] = conteudo
        elif titulo.startswith("COMO DEVO USAR"):
            fields["como_usar_medicamento"] = conteudo
        elif titulo.startswith("O QUE DEVO FAZER QUANDO EU ME ESQUECER"):
            fields["esqueceu_medicamento"] = conteudo
        elif titulo.startswith("QUAIS OS MALES"):
            fields["efeitos_colaterais"] = conteudo
        elif titulo.startswith("O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR"):
            fields["quantidade_a_mais"] = conteudo
        elif titulo.startswith("ONDE COMO E POR QUANTO TEMPO POSSO GUARDAR"):
            fields["como_guardar_medicamento"] = conteudo
    return fields


class Command(BaseCommand):
    help = "Carrega medicamentos (ANVISA) e bulas em uma única passagem"

    def handle(self, *args, **options):

        # ── 1. Carrega dados da ANVISA em memória ─────────────────────────────
        self.stdout.write("Carregando anvisa_data.json…")
        with open(ANVISA_JSON, "r") as f:
            json_data = json.load(f)

        # medication_id → {name, empresa, principio_ativo, classe_terapeutica}
        anvisa: dict[int, dict] = {}
        for elemento in json_data.get("data", []):
            if elemento[0] == "MEDICAMENTO" and elemento[9] == "VÁLIDO":
                med_id = int(elemento[4])
                anvisa[med_id] = {
                    "name":               elemento[1],
                    "empresa":            elemento[8],
                    "principio_ativo":    elemento[10],
                    "classe_terapeutica": elemento[7],
                }
        self.stdout.write(f"  {len(anvisa)} medicamentos válidos encontrados.")

        # ── 2. Carrega bulas dos 3 arquivos em memória ────────────────────────
        self.stdout.write("Carregando arquivos de bula…")
        bulas: dict[int, dict] = {}
        for path in BULARIO_JSONS:
            if not os.path.exists(path):
                self.stdout.write(self.style.WARNING(f"  Arquivo não encontrado: {path}"))
                continue
            with open(path, "r") as f:
                data = json.load(f)
            for key, var in data.items():
                med_id = int(key)
                bulas[med_id] = _parse_bula(var)
            self.stdout.write(f"  {path.split('/')[-1]}: {len(data)} bulas")

        self.stdout.write(f"  Total de bulas: {len(bulas)}")

        # ── 3. Cria/atualiza Medication linkando pelo medication_id ───────────
        self.stdout.write("Populando banco de dados…")
        criados    = 0
        atualizados = 0
        sem_bula   = 0

        for med_id, info in anvisa.items():
            bula = bulas.get(med_id, {})  # bula vazia se não encontrada
            if not bula:
                sem_bula += 1

            _, created = Medication.objects.update_or_create(
                medication_id=med_id,
                defaults={
                    **info,
                    **bula,
                }
            )
            if created:
                criados += 1
            else:
                atualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nConcluído: {criados} criados, {atualizados} atualizados, "
            f"{sem_bula} sem bula correspondente."
        ))