import pandas as pd
import json, os

def write_json(target_file, data):
    with open(os.path.join(f"{target_file}.json"), "w") as f:
        json.dump(data,f, indent=4, ensure_ascii=False)

name and dosage for medication register

#args: sheetname="", skiprow="", usecols=["",""]

df = pd.read_excel(r"Medicamentos x Especificacoes.xlsx",
                    usecols=["Doenca", "Apresentações"])
df = df.dropna()
df = df.set_index("Doenca")
df.to_excel("data/name_dosage.xlsx")

#informacoes essenciais:

df = pd.read_excel(r"Medicamentos x Especificacoes.xlsx",
                    usecols=["jk;", "Doenca", "Medicamento", "Apresentações", "Posologia"])
df = df.set_index("jk;")
df.to_excel("data/deaseade_medication.xlsx")

#transfor output into disctionary:

df = pd.read_excel(r"Medicamentos x Especificacoes.xlsx")
df = df.where(pd.notnull(df), None)
d = df.to_dict(orient="tight",index=False)
write_json("especialistas_as_dict", d)

#transforms a dataframe into json

df.to_json(path_or_buf="data/df_to_json", indent=4)