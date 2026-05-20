from medication.models import Leaflet, Medication_Name, Company, Active_Ingredient, Therapeutic_Class, Category, Brand, Medication, Dosage, Formato
from django.core.management.base import BaseCommand
from pathlib import Path
# from groq import Groq
import json,os

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
    def handle(self,*args,**options):
        cur = Path(__file__).resolve()
        root = cur.parent.parent.parent.parent.parent
        BASE = f"{root}/lembramed/api/src/anvisa_data/"
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
        self.stdout.write(f"{len(medicamentos)} medicamentos validos registrados.")
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
            __,_ = Medication.objects.update_or_create(
                medication_id = mid,
                defaults = {"process_num":clean_text(info.get("processo",""))}
            )
            if(clean_text(info.get("categoria",""))=="GENÉRICO"):
                _,n = Medication_Name.objects.update_or_create(
                    medication_id = mid,
                    defaults = {"name":clean_text(info.get("name",""))}
                )
            else:
                _,b = Brand.objects.update_or_create(
                    medication_id = mid,
                    defaults = {"brand":clean_text(info.get("name",""))}
                )
                
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

                # dosage_formato = clean_text(bul.get("como_usar_medicamento", ""))
                # if dosage_formato:
                #     extracted = extract_dosage_formato(dosage_formato, info.get("name", ""))
                    
                #     for dosage in extracted.get("dosages", []):
                #         Dosage.objects.update_or_create(
                #             medication_id= mid,
                #             defaults={"dosage": dosage}
                #         )
                #     for formato in extracted.get("formatos", []):
                #         Formato.objects.update_or_create(
                #             medication_id= mid,
                #             defaults={"formato": formato}
                #         )
        
            active_ingredients = clean_text(info.get('principio_ativo',"")).split(" + ")
            for principio_ativo in active_ingredients:
                _,ai = Active_Ingredient.objects.update_or_create(
                    medication_id = mid,
                    active_ingredient = clean_text(principio_ativo)
                )
            _,tc = Therapeutic_Class.objects.update_or_create(
                medication_id = mid,
                defaults = { 'therapeutic_class':clean_text(info.get('classe_terapeutica',""))}
            )
            _,co = Company.objects.update_or_create(
                medication_id = mid,
                defaults = {'company':clean_text(info.get('empresa',"").split(" - ",1)[-1])}
            )
            _,ca = Category.objects.update_or_create(
                medication_id = mid,
                defaults = {'category':clean_text(info.get('categoria'))}
            )
        self.stdout.write(self.style.SUCCESS(
            f"Concluído: {criados} criados, {atualizados} atualizados, {sem_bula} sem bula."
        ))