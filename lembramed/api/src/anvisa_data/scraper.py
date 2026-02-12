import fitz,re,os,json

def write_json(target_file, data):
    """Dumpa as informacoes em formato json e com acentuacoes"""
    with open(os.path.join(f"{target_file}.json"), "w") as f:
        json.dump(data,f, indent=4, ensure_ascii=False)

def get_pdf(pdf_path):
    """Returns a dictionary of topics extracted from each medication bula"""
    
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text() + "\n"

    # padrao_titulos = r"(\n(?:\d+\.|DIZERES|ANEXO)\s+[A-ZÀ-Ú\s\?\/]+(?=\n))"
    padrao_titulos = r"\n(\d+\.\s+[A-ZÀ-Ú0-9 ,\?\-]+)"

    if "DIZERES LEGAIS" in full_text:
        full_text = full_text.split("DIZERES LEGAIS")[0] + "DIZERES LEGAIS"

    partes = re.split(padrao_titulos, full_text)
    dados_estruturados = []

    if len(partes) > 1:
        for i in range(1, len(partes), 2):
            new_topic = {}
            titulo = partes[i]
            new_titulo = ""
            for t in titulo:
                if t.isalpha() or t == " ":
                    new_titulo+=t
            new_titulo = new_titulo.strip()
            conteudo = partes[i+1].strip() if i + 1 < len(partes) else ""
            new_topic['titulo'] = new_titulo
            new_topic['conteudo'] = conteudo
            dados_estruturados.append(new_topic)
    
    dados_estruturados = [ d for d in dados_estruturados 
                        if d["conteudo"].strip() != ""]

    return dados_estruturados

# resultado = get_pdf('data/bula_1770753006028.pdf')
# write_json("test5", resultado)