import json
from django.core.management.base import BaseCommand
# from medication.models import Medication

# file_path = "/home/yanetti/Desktop/extensao/server-medications/lembramed/api/src/anvisa_data/Titulos_teste.json"
# with open(file_path, 'r') as f:
#     data = json.load(f)
#     for key,var in data.items(): # key = register num, var = list of dicts (titulo:conteudo)
#         # print(f"key = {key}, var = {var}")
#         indicacoes_para_uso = ""
#         funcionamento_medicamento = ""
#         quando_nao_usar = ""
#         conhecimento_previo_necessario = ""
#         como_usar_medicamento = ""
#         esqueceu_medicamento = ""
#         efeitos_colaterais = ""
#         quantidade_a_mais = ""
#         como_guardar_medicamento = ""
#         for pares in var:
#             # print(f"{pares}\n\n")
#             # {'titulo': 'PARA QUE ESTE MEDICAMENTO É INDICADO', 
#             # 'conteudo': 'O aceclofenaco está indicado para o tratamento de processos dolorosos e inflamatórios tais como:  dores de dentes, traumatismos, dores musculares (ex: lombares), dores pós-cirúrgicas (após o parto  normal, após extração dentária), dores nas articulações dos ombros e reumatismos.   Também é eficaz no tratamento crônico de processos inflamatórios, como artrite reumatoide,  osteoartrite e espondilite anquilosante.'}
#             titulo = pares['titulo']
#             conteudo = pares['conteudo']
#             if titulo.startswith("PARA QUE ESTE MEDICAMENTO"):
#                 indicacoes_para_uso += conteudo
#             elif titulo.startswith("COMO ESTE MEDICAMENTO FUNCIONA"):
#                 funcionamento_medicamento += conteudo
#             elif titulo.startswith("QUANDO NÃO DEVO USAR ESTE MEDICAMENTO"):
#                 quando_nao_usar += conteudo
#             elif titulo.startswith("O QUE DEVO SABER ANTES DE USAR"):
#                 conhecimento_previo_necessario += conteudo
#             elif titulo.startswith("COMO DEVO USAR"):
#                 como_usar_medicamento += conteudo
#             elif titulo.startswith("O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR"):
#                 esqueceu_medicamento += conteudo
#             elif titulo.startswith("QUAIS OS MALES"):
#                 efeitos_colaterais += conteudo
#             elif titulo.startswith("O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR"):
#                 quantidade_a_mais += conteudo
#             elif titulo.startswith("ONDE COMO E POR QUANTO TEMPO POSSO GUARDAR"):
#                 como_guardar_medicamento += conteudo

# # print(f"indicacoes_para_uso = {indicacoes_para_uso}")

# ["155840398", "154230216", "154230123", "144930011",
#  "144930010", "141070007", "125680159", "123520100",
#  "118190216", "109740100", "109740092", "106890153",
#  "105830541", "105730609", "103900192", "103900141",
#  "102351059"]

# file_path = "/home/yanetti/Desktop/extensao/server-medications/lembramed/api/src/anvisa_data/Medicamentos_teste.json"
# with open (file_path, "r") as f:
#     data = json.load(f)
#     for data_colums,lista in data.items():
#         medication_id = ''
#         person_id = '1' #FALTA
#         DAYS_OF_WEEK = '__all__' #FALTA
#         # === ! === ! === ! === !
#         name = ''
#         dosage = '' #FALTA
#         time = '' #FALTA
#         begin = '' #FALTA
#         end = '' #FALTA
#         days = '' #FALTA
#         formato = '' #FALTA
#         quantity = '' #FALTA
#         empresa = ''
#         principio_ativo = ''
#         classe_terapeutica = ''
#         if data_colums == "data":
#             for elemento in lista:
#                 # print(f"{elemento}\n\n")
#                 if elemento[0] == 'MEDICAMENTO' and elemento[9] == 'VÁLIDO':
#                     name += elemento[1]
#                     medication_id += str(int(elemento[4]))
#                     empresa += elemento[8]
#                     principio_ativo += elemento[10]
#                     classe_terapeutica += elemento[7]
#         print(f"name={name},\n\n") 
#         print(f"medication_id={medication_id},\n\n,")
#         print(f"empresa={empresa},\n\n") 
#         print(f"principio_ativo={principio_ativo},\n\n") 
#         print(f"classe_terapeutica={classe_terapeutica}\n\n")
# print(int(102351059.0))

ids = [
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
    ]



# if (str(183260353) not in ids):
#     print("erro")
# else:
#     print("ta funfando")