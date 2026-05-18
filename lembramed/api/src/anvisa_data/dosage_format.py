import os,json
from google import genai
from dotenv import load_dotenv
from pathlib import Path

# export GEMINI_API_KEY=""
client = genai.Client()

arq = ["Bulario_medicamentos_iniciais0.json", "Bulario_medicamentos_iniciais1.json"]

def extract_text_to_be_parsed():
    """ Returns a dict with key = medication_id and value = COMO_USAR_MEDICAMENTO leaflet field
    of the respective med_id associated, for further use """
    res = {}
    for i in range(5):
        with open(f"Bulario_medicamentos_iniciais{i}.json", "r") as f:
            data = json.load(f)
            for mid,blocks in data.items():
                for titles in blocks:
                    if titles["titulo"]=="COMO DEVO USAR ESTE MEDICAMENTO":
                        res[str(mid)] = titles["conteudo"]
    return res

texts = extract_text_to_be_parsed()
for mid,text in texts.items():
    prompt = f"""
    Extract:
    - medication format
    - dosage

    Return ONLY JSON in this format:

    {{
        "medication_id": "{mid}",
        "format": "...",
        "dosage": ["..."]
    }}

    Text:
    {text}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt,
    )
    time.sleep(2)

# Error code: 429 (out of token)

# 183260353
# 170420025
# 105730675
# 183260458