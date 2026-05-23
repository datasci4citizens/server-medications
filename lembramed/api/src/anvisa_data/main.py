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

process_nums = [ # BETA
    "25351162018201424",
    "25351344662200710",
    "25351351960201170",
    "25351349629201830",
    "25351415294201930",##
    "25351415329201932",
    "25351214058200500",
    "25351111856202012",
    "25351764538201824",
    "25351471650201536",
    "253510244410011",  ##
    "2599200940964",    ##
    "253510128740123",  ##
    "25351066435200660",
    "25351595444201810",
    "25351089711201630",
    "25351312642200600",
    "25351419782200600",## 
    "25351338389201110",
    "25351010598201190",
    "25351308415200670",
    "25351498668201030",
    "25351671391201016",
    "25351346413201290",
    "25351331431201336",
    "25351278474201508",
    "25351072015201776",
    "25351407580201690",
    "25351674052201710",
    "25351097593201550",
    "25351653008201932",##
    "25351040441200852",
    "25351651342200930",
    "25351651785200910",##
    "25351680651201456",##
    "25351696761201476",##
    "25351688742201476",##
    "25351697819201416",
    "25351688499201424",
    "25351693624201470",##
    "25351664159201444",
    "25351688564201450",
    "25351696307201492",
    "25351699151201404",
    "25351693344201480",##
    "25351589163201336",
    "25351101205201716",
    "25351045797201810",
    "25351110114201844",
    "25351190092201970",##
    "25351190236202000",
    "25351838728201896",
    "25351627021201936",##
    "25351627163201900",
    "25351803928201828",
    "25351035604202150",
    "25351964686202496",
    "25351294508201412",
    "25351617747202348",
    "25351617278202370",
]

# process_nums = [ # com medication associated !!
#     "25351415294201930", "25351627021201936", "25351419782200600",
#     "25351653008201932", "25351651785200910", "25351680651201456",
#     "25351696761201476", "25351688742201476", "25351693624201470",
#     "25351693344201480", "25351190092201970", "253510244410011",
#     "2599200940964",     "253510128740123",
# ]

def write_json(target_file, data):
    """Dumpa as informacoes em formato json e com acentuacoes"""
    with open(os.path.join(f"{target_file}.json"), "w") as f:
        json.dump(data,f, indent=4, ensure_ascii=False)

# anvisa_dados = get_dict()
# process_nums = [
#     str(dados[6]) for dados in anvisa_dados.get("data",[]) if dados[6]
# ]

run_scraper(process_nums=process_nums)