from web_navigator import download_bula, get_last_downloaded_file
from scraper import get_pdf, write_json
from excel_treatment import get_dict

# abrir o json "anvisa_data.json" em 'data' e pegar o 
# [4] de cada lista === registerNum
anvisa_dados = get_dict()
for key,value in anvisa_dados.items():
    if (key == 'data'):
        registerNums = [f'{int(dados[4])}' for dados in 
        value if dados[4]]

# output json do tipo:
# {RegisterNum1: 
#     [
#         {   title: xxx 
#             conteudo: xxx
#         },
#     ]
# }
data = {}

# Pega a bula do paciente de todos os medicamentos registrados no excel da anvisa
for num in registerNums:
    if download_bula(num) == 0:
        continue
    file_name = get_last_downloaded_file("data/")
    data[num] = get_pdf(f"data/{file_name}")

# Salva os dados 
write_json("Bulario_data", data)

# for num in registerNums:
#     print(num)
# print(f'Penultimo elemento: {registerNums[-2]},\nUltimo elemento: {registerNums[-1]}')