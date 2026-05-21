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

# ids = [
#         "183260353", "178170028", "143810218", "100431203", "183260248",
#         "155370012", "183260002", "183260318", "183260145", "178170047",
#         "186200020", "167730576", "183260101", "167730407", "167730405",
#         "167730536", "183260422", "155370009", "167730590", "183260028",
#         "104070111", "104070112", "162410018", "116180106", "186200018",
#         "162410009", "186100006", "167730552", "167730278", "183260260",
#         "183260129", "167730639", "183260289", "183260503", "105730780",
#         "183260366", "106460207", "183260293", "170560048", "104971323",
#         "103670160", "183260487", "183260472", "155370057", "104070105",
#         "183260048", "183260155", "154230266", "183260430", "155840500",
#         "105710158", "183260136", "183260294", "141070059", "183260126",
#         "135690015", "103900182", "167730440", "183260035", "138410004",
#     ]

# if (str(183260353) not in ids):
#     print("erro")
# else:
#     print("ta funfando")

# with open("teste.json", "r+") as f:
#     data = json.load(f)
#     content.json.update("teste")
#     file.seek(0)
#     json.dump(data, f, indent=4)

# with open('Bulario_medicamentos_iniciais0.json') as f0, open('Bulario_medicamentos_iniciais1.json') as f1, open('Bulario_medicamentos_iniciais2.json') as f2, open('Bulario_medicamentos_iniciais3.json') as f3, open('Bulario_medicamentos_iniciais4.json') as f4:
#     data0 = json.load(f0)
#     data1 = json.load(f1)
#     data2 = json.load(f2)
#     data3 = json.load(f3)
#     data4 = json.load(f4)

# merged = {**data0, **data1, **data2, **data3, **data4}
# with open('Leaflets.json', 'w') as out:
#     json.dump(merged, out, indent=4)

# DUMPS THE CONTENTS OF THE JSON FILES INTO A SINGLE ONE AS ELEMENTS OF A LIST #

# with open('Leaflets.json', 'w') as out:
#     json.dump([data0, data1, data2, data3, data4], out, indent=4,ensure_ascii=False)

# _,med = Medication.objects.update_or_create(
#             medication_id = 144930011,
#             process_num = 253510001840168
#         )
# TESTE = "BETAÍNA +  CITRATO DE COLINA +  DL-METIONINA +  LEVOMETIONINA"
# active_ingredients = TESTE.split(" + ")
# for i in active_ingredients:
#     _,ai = Active_Ingredient.objects.update_or_create(
#         medication_id = 144930011,
#         active_ingredient = i.strip()
#     )

# s = "A INDICADA DESTE MEDICAMENTO?  A dose segura para o ferro é de 65 mg/dia para pacientes adultos e, para crianças, 2,0  mg/kg de peso corpóreo até o limite de 50 mg/dia. Acima destes valores, recomenda-se  utilizar o produto somente sob prescrição médica.         Em caso de superdosagem, recomenda-se "
# g = "MEDICAMENTO?  Caso haja esquecimento da ingestão de uma dose deste medicamento, retomar a  posologias sem a necessidade de suplementação."
# teste = g.split("?")
# print(teste)
# print()
# print(teste[-1].strip())

# Total bulas validas: 15460
# [
#     {'titulo': 'PARA QUE ESTE MEDICAMENTO É INDICADO', 'conteudo': 'A SAÚDE DA MULHER® é indicado como regulador menstrual, nas cólicas menstruais, perturbações da  menopausa e manifestações agudas ou crônicas das dismenorreias (cólicas menstruais), nas irregularidades  do fluxo menstrual.'},
#     {'titulo': 'COMO ESTE MEDICAMENTO FUNCIONA', 'conteudo': 'A SAÚDE DA MULHER® atua como antiespasmódico (previne a ocorrência de contrações de um músculo)  e anticolinérgico (inibe as ações da acetilcolina, que é um neurotransmissor encontrado no sistema nervoso).'},
#     {'titulo': 'QUANDO NÃO DEVO USAR ESTE MEDICAMENTO', 'conteudo': 'Este produto é contraindicado na presença de doença renal e em casos de hipersensibilidade a algum  componente da fórmula.  Este medicamento é contraindicado em caso de suspeita de dengue, pois pode aumentar o risco de  sangramentos.  Não use este medicamento caso tenha histórico de asma causada por uso anterior deste ou de outro  medicamento com ação parecida ou caso tenha problemas no estômago.'},
#     {'titulo': 'O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO', 'conteudo': 'Não é aconselhado o uso de A SAÚDE DA MULHER® durante a gravidez.  Este medicamento não deve ser utilizado por mulheres grávidas sem orientação médica ou do  cirurgião-dentista. A SAÚDE DA MULHER® pode potencializar os efeitos de medicamentos sedativos e  anticoagulantes, não devendo ser administrado concomitantemente com medicamentos destas classes.  Uso contraindicado no aleitamento ou na doação de leite humano. Este medicamento é contraindicado  durante o aleitamento ou doação de leite, pois pode ser excretado no leite humano e pode causar  reações indesejáveis no bebê. Seu médico ou cirurgião-dentista deve apresentar alternativas para o seu  tratamento ou para a alimentação do bebê.  Atenção: contém o corante caramelo.  O uso de ácido acetilsalicílico pode causar a Síndrome de Reye, uma doença rara, mas grave, em  crianças ou adolescentes com sintomas gripais ou catapora.     O tratamento com este medicamento não deve se prolongar por mais de 7 dias, a menos que  recomendado pelo médico, pois pode causar problemas nos rins, estômago, intestino, coração e vasos  sanguíneos.  Este medicamento contém 4,33% de álcool (etanol) e pode causar intoxicação, especialmente em  crianças.  Informe ao seu médico ou cirurgião-dentista se você está fazendo uso de algum outro medicamento.'}, 
#     {'titulo': 'COMO DEVO USAR ESTE MEDICAMENTO', 'conteudo': "Deve-se tomar A SAÚDE DA MULHER® por via oral, sempre diluído em meio copo d'água. Nas  irregularidades do fluxo menstrual (iniciando o tratamento 15 dias após o término da menstruação) e nas  perturbações na menopausa, tomar 1 copo-medida duas vezes ao dia (a cada 12 horas) durante 7 dias. Nos  casos de cólicas menstruais, tomar durante a menstruação 1 copo-medida três vezes ao dia (a cada 8 horas).  Nos casos de inflamações e hemorragias uterinas tomar 1 copo-medida 4 vezes ao dia (a cada 6 horas) até o  alívio dos sintomas.  Siga corretamente o modo de usar. Em caso de dúvidas sobre este medicamento, procure orientação  do farmacêutico. Não desaparecendo os sintomas, procure orientação de seu médico ou cirurgião- dentista."},
#     {'titulo': 'O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO', 'conteudo': 'Tome a dose assim que se lembrar dela. Entretanto, se estiver próximo ao horário da dose seguinte, salte a  dose esquecida e continue o tratamento conforme prescrito. Não utilize o dobro da dose para compensar uma  dose esquecida.  Em caso de dúvidas, procure orientação do farmacêutico ou de seu médico, ou cirurgião-dentista.'},
#     {'titulo': 'QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR', 'conteudo': 'A SAÚDE DA MULHER® pode, ocasionalmente, causar algumas reações adversas, tais como: queda da  pressão sanguínea, aumento do número de evacuações, diarreias, sonolência e náuseas.  Informe ao seu médico, cirurgião-dentista ou farmacêutico o aparecimento de reações indesejáveis  pelo uso do medicamento. Informe também à empresa através do seu serviço de atendimento.'}, 
#     {'titulo': 'O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA', 'conteudo': 'DESTE MEDICAMENTO?  Não existe casos conhecidos de superdosagem deste medicamento, em caso de ingestão de grande  quantidade deste medicamento, deve-se procurar auxílio no centro de saúde mais próximo.  Em caso de uso de grande quantidade deste medicamento, procure rapidamente socorro médico e leve  a embalagem ou bula do medicamento, se possível. Ligue para 0800 722 6001, se você precisar de mais  orientações.    III - DIZERES LEGAIS'}
# ]