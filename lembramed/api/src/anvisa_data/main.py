from web_navigator import download_bula, get_last_downloaded_file
from scraper import get_pdf, write_json
from excel_treatment import get_dict
import os

# abrir o json "anvisa_data.json" em 'data' e pegar o 
# [4] de cada lista === registerNum
anvisa_dados = get_dict()
for key,value in anvisa_dados.items():
    if (key == 'data'):
        registerNums = [f'{int(dados[4])}' for dados in 
        value if dados[4]]
#         teste = 0
#         registerNums = []
#         for dados in value:
#             if dados[4]:
#                 registerNums.append(f'{int(dados[4])}')
#                 teste += 1
#                 if teste >= 20:
#                     break
# registerNums = [
# "103900123",
# "141070007",
# "105730462",
# "145870004",
# "105730723",
# "105530338",
# "105710037",
# "100890254",
# "103720263",
# "178170882",
# "102350655",
# "178170818",
# "102350659",
# "126750331",
# "183260433",
# "103700096",
# "116180250",
# "105730566",
# "144930010",
# "109740273",
# "102350404",
# "104540167",
# "105730611",
# "102350563",
# "103720281",
# "178170854",
# "109740285",
# "105710006",
# "103900143",
# "103720179",
# "102350492",
# "104540207",
# "105730388",
# "102350515",
# "103720308",
# "178170832",
# "109740233",
# "105710019",
# "103900099",
# "103720297",
# "102350547",
# "104540189",
# "105730644",
# "102350578",
# "103720334",
# "178170861",
# "109740244",
# "105710041",
# "103900154",
# "103720265",
# "102350503",
# "104540211",
# "105730671",
# "102350589",
# "103720346",
# "178170874",
# "109740256",
# "105710052",
# ]
data = {}
# Pega a bula do paciente de todos os medicamentos registrados no excel da anvisa
for num in registerNums:
    if download_bula(num) == 1:
        continue
    file_name = get_last_downloaded_file("data/")
    if file_name != None:
        dados = get_pdf(f"data/{file_name}")
        if dados != []:
            data[num] = dados
        os.remove(f"data/{file_name}")

write_json("Bulario_medicamentos_iniciais", data)

# pip install --upgrade certifi "urllib3[socks]"
# pip install --upgrade selenium
# pip install chardet
# pip install PyMuPDF