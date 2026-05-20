from web_navigator import run_batch
from scraper import get_pdf, write_json
from excel_treatment import get_dict
import os
from dosage_format import *

# DOWNLOAD_DIR = os.path.abspath("data")
# DOWNLOAD_DIR = "data/"
# OUTPUT_NAME  = "Bulario_medicamentos_iniciais_continuacao"

# os.makedirs(DOWNLOAD_DIR, exist_ok=True)
# anvisa_dados = get_dict()
# register_nums = [
#     f"{int(dados[4])}"
#     for dados in anvisa_dados.get("data", [])
#     if dados[4]
# ]

# data = {}

# run_batch(
#     register_nums=register_nums,
#     download_dir=DOWNLOAD_DIR,
#     process_fn=get_pdf,      
#     output_dict=data,
# )

# write_json(OUTPUT_NAME, data)
# print(f"Done. {len(data)} leaflets written to {OUTPUT_NAME}.json")

def write_json(target_file, data):
    """Dumpa as informacoes em formato json e com acentuacoes"""
    with open(os.path.join(f"{target_file}.json"), "w") as f:
        json.dump(data,f, indent=4, ensure_ascii=False)

anvisa_dados = get_dict()
process_nums = [
    dados[6] for dados in anvisa_dados.get("data",[]) if dados[6]
]
data = {}
run_scraper(
    process_nums=process_nums,
    output_dict=data
)

with open(os.path.join(f"Dosage_Formato.json"),"r+") as f:
    cur = json.load(f)
    cur.update(data)
    f.seek(0)
    json.dump(cur,f,indent=4)

print(f"Process finished, {len(data)} medications parsed written to Dosage_Formato.json")