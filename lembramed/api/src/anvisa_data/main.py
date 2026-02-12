from web_navigator import download_bula
from excel_treatment import get_dict

# abrir o json "anvisa_data.json" em 'data' e pegar o 
# [4] de cada lista === registerNum

anvisa_dados = get_dict()
for key,value in anvisa_dados.items():
    if (key == 'data'):
        registerNums = [f'{int(dados[4])}' for dados in 
        value if dados[4]]

# for num in registerNums:
#     print(num)

# print(f'Penultimo elemento: {registerNums[-2]},\nUltimo elemento: {registerNums[-1]}')

# Pega a bula do paciente de todos os medicamentos registrados no excel da anvisa
for num in registerNums:
    get_bula(num)