import fitz,re,os,json

def write_json(target_file, data):
    """Dumpa as informacoes em formato json e com acentuacoes"""
    with open(os.path.join(f"{target_file}.json"), "w") as f:
        json.dump(data,f, indent=4, ensure_ascii=False)

# def clean_bula_text(text):
#     # remove hifenização de final de linha
#     text = re.sub(r'-\n\s*', '', text)

#     # junta palavras quebradas por newline (he\nmorragia)
#     text = re.sub(r'([a-zà-ú])\n([a-zà-ú])', r'\1\2', text, flags=re.IGNORECASE)

#     # junta linhas que continuam frase
#     text = re.sub(r'\n(?=[a-zà-ú])', ' ', text, flags=re.IGNORECASE)

#     # remove múltiplas quebras
#     text = re.sub(r'\n+', '\n', text)

#     # remove múltiplos espaços
#     text = re.sub(r'[ \t]+', ' ', text)

#     return text.strip()

def is_valid_title(titulo):
    KNOWN_TITLES = [
    "PARA QUE ESTE MEDICAMENTO",
    "COMO ESTE MEDICAMENTO FUNCIONA",
    "QUANDO NÃO DEVO USAR",
    "O QUE DEVO SABER ANTES",
    "ONDE COMO E POR QUANTO TEMPO POSSO GUARDAR",
    "COMO DEVO USAR",
    "O QUE DEVO FAZER QUANDO EU ME ESQUECER",
    "QUAIS OS MALES",
    "O QUE FAZER SE ALGUÉM USAR"
    ]

    upper = [c for c in titulo if c.isupper()]
    if not upper:
        return False

    if len(titulo.split()) > 15:
        return False

    titulo = titulo.upper()
    for k in KNOWN_TITLES:
        if k in titulo:
            return True

    return False

def get_pdf(pdf_path):
    """Returns a dictionary of topics extracted from each medication bula"""
    
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text() + "\n"

    # full_text = clean_bula_text(full_text)

    # padrao_titulos = r"(\n(?:\d+\.|DIZERES|ANEXO)\s+[A-ZÀ-Ú\s\?\/]+(?=\n))"
    # padrao_titulos = r"\n(\d+\.\s+[A-ZÀ-Ú0-9 ,\?\-]+)"
    # padrao_titulos = r"\n(\d+\.\s+[A-ZÀ-Ú0-9 ,\?\-]{10,})\n"
    # padrao_titulos = r"\b(\d{1,2}\.\s+[A-ZÀ-Ú][A-ZÀ-Ú0-9 ,\-?]{8,})"
    padrao_titulos = r"\n(\d{1,2}\s*[\.\-–]?\s*[A-ZÀ-Ú][A-ZÀ-Ú0-9 ,\?\-]{8,})"

    if "DIZERES LEGAIS" in full_text:
        full_text = full_text.split("DIZERES LEGAIS")[0] + "DIZERES LEGAIS"

    partes = re.split(padrao_titulos, full_text)
    dados_estruturados = []

    if len(partes) > 1:
        for i in range(1, len(partes), 2):
            new_topic = {}
            if (is_valid_title(partes[i])):
                titulo = partes[i]
            else:
                continue
            new_titulo = ""
            for t in titulo:
                if t.isalpha() or t == " ":
                    new_titulo+=t
            new_titulo = new_titulo.strip()
            conteudo = partes[i+1].replace("\n", " ").strip() if i + 1 < len(partes) else ""
            # conteudo = clean_bula_text(conteudo)
            new_topic['titulo'] = new_titulo
            new_topic['conteudo'] = conteudo
            dados_estruturados.append(new_topic)
    
    dados_estruturados = [ d for d in dados_estruturados 
                        if d["conteudo"].strip() != ""]

    return dados_estruturados

# resultado = get_pdf('data/bula_1770753006028.pdf')
# write_json("test5", resultado)