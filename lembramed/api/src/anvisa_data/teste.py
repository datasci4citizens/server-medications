import pandas as pd 
import chardet, json, os

def write_json(target_file, data):
    with open(os.path.join(f"{target_file}.json"), "w") as f:
        json.dump(data,f, indent=4, ensure_ascii=False)

# USAR UTF-8-SIG E NO BANCO (utf8mb4 ou Latin1)

# with open('DADOS_ABERTOS_MEDICAMENTOS.csv', 'rb') as f:
#     result = chardet.detect(f.read(100000))
#     print(result) #{'encoding': 'utf-8', 'confidence': 0.99, 'language': ''} TRATAD

df = pd.read_csv(r"DADOS_ABERTOS_MEDICAMENTOS.csv", sep=';', encoding='cp1252')
df.columns = df.columns.str.strip()
df = df.dropna()
# print(df) 

#d = df.to_json(indent=4, date_format='iso')
d = df.to_dict(orient='tight', index=False)

write_json("anvisa_data", d)

#df = df = df.set_index("TIPO_PRODUTO")
#df.to_excel("anvisa_dados.xlsx", index=False)
#{'encoding': 'ISO-8859-1', 'confidence': 0.73, 'language': ''} NAO TRATADO

# df = pd.read_csv(r"DADOS_ABERTOS_MEDICAMENTOS.csv",
#                 usecols=["TIPO_PRODUTO", "NOME_PRODUTO",
#                 "NUMERO_REGISTRO_PRODUTO", "CLASSE_TERAPEUTICA",
#                 "EMPRESA_DETENTORA_REGISTRO", "SITUACAO_REGISTRO",
#                 "PRINCIPIO_ATIVO"], encoding="utf-8")

# Fazer scraping do Bulário Eletrônico da ANVISA 
#(que tem as bulas em PDF/HTML) para extrair o texto 
# de interações.
# 'https://consultas.anvisa.gov.br/#/bulario/'