from medication.models import (
    Leaflet, Medication_Name, Company, Active_Ingredient,
    Therapeutic_Class, Category, Brand, Medication, Formato, 
    AnvisaRegister, Presentation, DosageIngredients,
)

import calendar
from datetime import date
from django.core.management.base import BaseCommand
from pathlib import Path
# from groq import Groq
import json,os,re

### YOU MIGHT HAVE TO "pip install groq" ON TERMINAL TO RUN THIS ###
### MIGHT AS WELL CREATE AND USE A GROQ_API_KEY FOR FREE ONLINE  ###
### USE: https://console.groq.com/keys TO CREATE A PROJECT & KEY ###

# client = Groq(api_key=os.environ["GROQ_API_KEY"])

# def extract_dosage_formato(conteudo: str, med_name: str) -> dict:
#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[{
#             "role": "user",
#             "content": f"""Leia o texto abaixo e retorne SOMENTE um JSON com:
#             - "dosages": lista de dosagens encontradas (ex: ["500mg", "1g"])
#             - "formatos": lista de formas farmacêuticas (ex: ["Comprimido", "Solução oral"])

#             Texto:
#             {conteudo}
#             Retorne apenas o JSON, sem texto adicional."""
#         }]
#     )
#     try:
#         text = response.choices[0].message.content.strip()
#         text = text.replace("```json","").replace("```","")
#         return json.loads(text)
#     except json.JSONDecodeError:
#         return {"dosages": [], "formatos": []}

FORMATO_RULES = (
    ("adesivo transdermico", re.compile(r"\bADES\s+TRANSD\b")),
    ("injetavel", re.compile(r"\b(?:SOL|SUS)\s+INJ\b")),
    ("inalatorio", re.compile(r"\b(?:P[ÓO]\s+)?INAL\b")),
    ("colirio", re.compile(r"\b(?:COL[ÍI]RIO|SOL\s+OFT)\b")),
    ("supositorio", re.compile(r"\bSUP(?:\s+RET)?\b")),
    ("capsula", re.compile(r"\bCAP\b")),
    ("comprimido", re.compile(r"\bCOM\b")),
    ("pomada", re.compile(r"\b(?:POM|UNG|CREM|GEL)\b")),
    ("liquido", re.compile(r"\b(?:XPE|SOL|SUS)\b")),
    ("granulado", re.compile(r"\bGRAN\b")),
)

class Command(BaseCommand):
    help = "Load beta medications and related data into the initial databse"
    ids = {
        "183260353", "178170028", "143810218", "100431203", "183260248",
        "155370012", "183260002", "183260318", "183260145", "178170047",
        "186200020", "167730576", "183260101", "167730407", "167730405",
        "167730536", "183260422", "155370009", "167730590", "183260028",
        "104070111", "104070112", "162410018", "116180106", "186200018",
        "162410009", "186100006", "167730552", "167730278", "183260260",
        "183260129", "167730639", "183260289", "183260503", "105730780",
        "183260366", "106460207", "183260293", "170560048", "104971323",
        "103670160", "183260487", "183260472", "155370057", "104070105",
        "183260048", "183260155", "154230266", "183260430", "155840500",
        "105710158", "183260136", "183260294", "141070059", "183260126",
        "135690015", "103900182", "167730440", "183260035", "138410004",
    }

    def extract_formato(self, dosage: str) -> str | None:
        normalized = re.sub(r"\s+", " ", (dosage or "").upper()).strip()

        for formato, pattern in FORMATO_RULES:
            if pattern.search(normalized):
                return formato

        return None

    def parse_expiration_month(self, value: str) -> date:
        month, year = map(int, value.strip().split("/"))
        return date(year, month, calendar.monthrange(year, month)[1])

    def handle(self,*args,**options):
        cur = Path(__file__).resolve()
        root = cur.parent.parent.parent.parent.parent
        BASE = f"{root}/lembramed/api/src/anvisa_data/"
        mid_pn = {} # medication_id : process_num to make so its possible to search in presentations
        medicamentos = {}
        with open(os.path.join(BASE,"anvisa_data.json"),"r",encoding="utf-8")as f:
            json_data=json.load(f)
        for elemento in json_data.get("data",[]):
            if elemento[0] != "MEDICAMENTO" or elemento[9] != "VÁLIDO":
                continue
            if str(int(elemento[4])) not in self.ids:
                continue
            medicamentos[int(elemento[4])]={
                "name":elemento[1],
                "categoria":elemento[3],
                "processo":elemento[6],
                "classe_terapeutica":elemento[7],
                "empresa":elemento[8],
                "principio_ativo":elemento[10],
            }
            mid_pn[int(elemento[4])] = elemento[6]
        self.stdout.write(f"Medicamentos validos registrados: {len(medicamentos)} ")
        bula = {}

        # for i in range(5):
        #     path = os.path.join(BASE, f"Bulario_medicamentos_iniciais{i}.json")
        #     with open(path, "r",encoding="utf-8") as f:
        #         data = json.load(f)
        #     bula.update(data)

        with open(os.path.join(BASE, "leaflets.json"),"r",encoding="utf-8") as f:
            data = json.load(f)
        bula.update(data)
        bulas = {}
        for mid in self.ids:
            bula_data = bula.get(str(mid),"")
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
            for pares in bula_data:
                titulo  = pares["titulo"]
                conteudo = pares["conteudo"]
                if titulo.startswith("PARA QUE ESTE MEDICAMENTO"):
                    campos["indicacoes_para_uso"] = conteudo
                elif titulo.startswith("COMO ESTE MEDICAMENTO FUNCIONA"):
                    campos["funcionamento_medicamento"] = conteudo
                elif titulo.startswith("QUANDO NÃO DEVO USAR"):
                    campos["quando_nao_usar"] = conteudo
                elif titulo.startswith("O QUE DEVO SABER ANTES DE USAR"): # PRECAUÇÕES E ADVERTÊNCIAS
                    campos["conhecimento_previo_necessario"] = conteudo
                elif titulo.startswith("COMO DEVO USAR"):
                    campos["como_usar_medicamento"] = conteudo
                elif titulo.startswith("O QUE DEVO FAZER QUANDO EU ME ESQUECER"): # MEDICAMENTO, split("?")
                    if conteudo.startswith("MEDICAMENTO?"):
                        t = conteudo.split("?")
                        campos["esqueceu_medicamento"] = t[-1].strip()
                    else:
                        campos["esqueceu_medicamento"] = conteudo
                elif titulo.startswith("QUAIS OS MALES"):
                    campos["efeitos_colaterais"] = conteudo
                elif titulo.startswith(("O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR", "O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DESTE MEDICAMENTO?", "O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR MEDICAMENTO")):
                    if conteudo.startswith(("DESTE MEDICAMENTO?", "INDICADA DESTE MEDICAMENTO?", "MEDICAMENTO", "A INDICADA DESTE MEDICAMENTO?")):
                        t = conteudo.split("?")
                        campos["quantidade_a_mais"] = t[-1].strip()
                    else:
                        campos["quantidade_a_mais"] = conteudo
                elif titulo.startswith("ONDE COMO E POR QUANTO TEMPO POSSO GUARDAR"):
                    campos["como_guardar_medicamento"] = conteudo
            bulas[mid] = campos
        self.stdout.write(f"Total bulas preenchidas: {len(bulas)}")

        def clean_text(text):
            if not text:
                return ""
            return str(text).replace('\x00', '')

        criados = atualizados = sem_bula = 0

        for mid, info in medicamentos.items():

            medication,created = Medication.objects.update_or_create( # Brand/Name and multiple pointers to active ingredients
                medication_id = mid,
                process_num = clean_text(info.get('processo',""))
            )

            if(created == False):
                continue

            tc,_ = Therapeutic_Class.objects.get_or_create(
                therapeutic_class = clean_text(info.get('classe_terapeutica',""))
            )
            medication.therapeutic_class = tc
            co,_ = Company.objects.get_or_create(
                company = clean_text(info.get('empresa',"").split(" - ",1)[-1])
            )
            medication.company = co
            ca,_ = Category.objects.get_or_create(
                category = clean_text(info.get('categoria'))
            )
            medication.category = ca

            medication.save()

            bul = bulas.get(str(mid), {})
            if not bul:
                sem_bula += 1
            else:
                _, created = Leaflet.objects.update_or_create(
                    medication_id =  mid,
                    defaults = {
                        "indicacoes_para_uso":clean_text(bul.get("indicacoes_para_uso", "")),
                        "funcionamento_medicamento":clean_text(bul.get("funcionamento_medicamento", "")),
                        "quando_nao_usar":clean_text(bul.get("quando_nao_usar", "")),
                        "conhecimento_previo_necessario":clean_text(bul.get("conhecimento_previo_necessario", "")),
                        "como_usar_medicamento":clean_text(bul.get("como_usar_medicamento", "")),
                        "esqueceu_medicamento":clean_text(bul.get("esqueceu_medicamento", "")),
                        "efeitos_colaterais":clean_text(bul.get("efeitos_colaterais", "")),
                        "quantidade_a_mais":clean_text(bul.get("quantidade_a_mais", "")),
                        "como_guardar_medicamento":clean_text(bul.get("como_guardar_medicamento", ""))
                    }
                )
                if created:
                    criados += 1
                else:
                    atualizados += 1

            if(clean_text(info.get("categoria",""))=="GENÉRICO"):
                medication_name,_ = Medication_Name.objects.update_or_create(
                    name = clean_text(info.get("name",""))
                )
                medication.name = medication_name
            else:
                medication_brand,_ = Brand.objects.update_or_create(
                    brand = clean_text(info.get("name",""))
                )
                medication.brand = medication_brand
                
            active_ingredients = clean_text(info.get('principio_ativo',"")).split(" + ")
            for principio_ativo in active_ingredients:
                ai,_ = Active_Ingredient.objects.get_or_create(
                    active_ingredient = clean_text(principio_ativo)
                )
                medication.active_ingredients.add(ai)

            medication.save()

        self.stdout.write(self.style.SUCCESS(
            f"Leaflets: {criados} criados, {atualizados} atualizados, {sem_bula} sem bula."
        ))

        pata = {}
        with open(os.path.join(BASE, "presentations.json"),"r",encoding="utf-8") as f:
            data = json.load(f)
        pata.update(data)

        # for id,pn in mid_pn.items():
        #     cur = pata.get(str(pn), "")
        #     for id,object in cur["presentations"].items():
        #         print (object["dosage"])

        criados = 0
        atualizados = 0
        presentations = {}
        anregisters = {}
        di = {}

        for id,pn in mid_pn.items():
            cur = pata.get(str(pn), "")
            cdi = {}

            ar,_ = AnvisaRegister.objects.update_or_create(
                register_num = id,
                defaults={
                    "process_num":pn,
                    "expiration_date": self.parse_expiration_month(cur["expiration_date"])
                }
            )

            for key,value in cur["presentations"].items():
                formato,_ = Formato.objects.get_or_create(
                        formato = self.extract_formato(value["dosage"])
                )
                presentation,created = Presentation.objects.update_or_create(
                    regulation_num = key,
                    defaults={
                        "register": ar,
                        "formato": formato,
                        "dosage": value["dosage"],
                        "embalagem": value["embalagem"],
                        "administration" : value["administration"],
                        "conservation" : value["conservation"],
                        "prescription_restriction" : value["prescription_restriction"],
                        "usage_restriction" : value["usage_restriction"],
                        "label" : value["label"],
                        "can_be_fractioned" : value["can_be_fractioned"]
                    }
                )

                if not created:
                    atualizados += 1
                else:
                    criados += 1

                for order,ai in enumerate(value["concentration_order"],1):
                    # checar se ai esta no banco => get or create
                    
                    aii,_ = Active_Ingredient.objects.get_or_create(
                        active_ingredient = ai
                    )

                    DosageIngredients.objects.update_or_create(
                        presentation = presentation,
                        active_ingredient = aii,
                        defaults={
                            "order":order
                        },
                    )

        self.stdout.write(self.style.SUCCESS(
                    f"Presentations: {criados} criados, {atualizados} atualizados"
        ))