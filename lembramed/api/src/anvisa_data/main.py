from web_navigator import run_batch
from scraper import get_pdf, write_json
from excel_treatment import get_dict
import os

DOWNLOAD_DIR = os.path.abspath("data")
DOWNLOAD_DIR = "data/"
OUTPUT_NAME  = "Bulario_medicamentos_iniciais_continuacao"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
anvisa_dados = get_dict()
register_nums = [
    f"{int(dados[4])}"
    for dados in anvisa_dados.get("data", [])
    if dados[4]
]

data = {}

run_batch(
    register_nums=register_nums,
    download_dir=DOWNLOAD_DIR,
    process_fn=get_pdf,      
    output_dict=data,
)

write_json(OUTPUT_NAME, data)
print(f"Done. {len(data)} leaflets written to {OUTPUT_NAME}.json")