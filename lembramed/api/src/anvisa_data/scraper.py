import fitz,re,os,json

def write_json(target_file, data):
    """Dumpa as informacoes em formato json e com acentuacoes"""
    with open(os.path.join(f"{target_file}.json"), "w") as f:
        json.dump(data,f, indent=4, ensure_ascii=False)

def get_pdf(pdf_path):
    """Returns a dictionary of topics extracted from each medication bula"""
    
    # text = "\n".join(
    #     p.get_textpage().get_text_range() 
    #     for p in pdfium.PdfDocument(f"{pdf_path}")
    # )
    # print(text)
    
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text() + "\n"

    padrao_titulos = r"(\n(?:\d+\.|DIZERES|ANEXO)\s+[A-ZÀ-Ú\s\?\/]+(?=\n))"
    partes = re.split(padrao_titulos, full_text)
    dados_estruturados = {}

    if len(partes) > 1:
        for i in range(1, len(partes), 2):
            titulo = partes[i].strip()
            conteudo = partes[i+1].strip() if i + 1 < len(partes) else ""
            dados_estruturados[titulo] = conteudo
    return dados_estruturados

resultado = get_pdf('data/bula_1770753006028.pdf')
write_json("test", resultado)