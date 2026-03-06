from web_navigator import download_bula, get_last_downloaded_file
from scraper import get_pdf, write_json
from excel_treatment import get_dict
import os

# abrir o json "anvisa_data.json" em 'data' e pegar o 
# [4] de cada lista === registerNum
anvisa_dados = get_dict()
for key,value in anvisa_dados.items():
    if (key == 'data'):
        # registerNums = [f'{int(dados[4])}' for dados in 
        # value if dados[4]]
        teste = 0
        registerNums = []
        for dados in value:
            if dados[4]:
                registerNums.append(f'{int(dados[4])}')
                teste += 1
                if teste >= 20:
                    break

data = {}

# Pega a bula do paciente de todos os medicamentos registrados no excel da anvisa
for num in registerNums:
    if download_bula(num) == 1:
        continue
    file_name = get_last_downloaded_file("data/")
    if file_name != None:
        data[num] = get_pdf(f"data/{file_name}")
        os.remove(f"data/{file_name}")

write_json("Bulario_data_teste", data)