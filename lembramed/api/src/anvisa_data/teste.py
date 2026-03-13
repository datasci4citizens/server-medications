import json

file_path = "/home/yanetti/Desktop/extensao/server-medications/lembramed/api/src/anvisa_data/Titulos_teste.json"
with open(file_path, 'r') as f:
    data = json.load(f)
    for key,var in data.items(): # key = register num, var = list of dicts (titulo:conteudo)
        # print(f"key = {key}, var = {var}")
        indicacoes_para_uso = ""
        funcionamento_medicamento = ""
        quando_nao_usar = ""
        conhecimento_previo_necessario = ""
        como_usar_medicamento = ""
        esqueceu_medicamento = ""
        efeitos_colaterais = ""
        quantidade_a_mais = ""
        como_guardar_medicamento = ""
        for pares in var:
            # print(f"{pares}\n\n")
            # {'titulo': 'PARA QUE ESTE MEDICAMENTO É INDICADO', 
            # 'conteudo': 'O aceclofenaco está indicado para o tratamento de processos dolorosos e inflamatórios tais como:  dores de dentes, traumatismos, dores musculares (ex: lombares), dores pós-cirúrgicas (após o parto  normal, após extração dentária), dores nas articulações dos ombros e reumatismos.   Também é eficaz no tratamento crônico de processos inflamatórios, como artrite reumatoide,  osteoartrite e espondilite anquilosante.'}
            titulo = pares['titulo']
            conteudo = pares['conteudo']
            if titulo.startswith("PARA QUE ESTE MEDICAMENTO"):
                indicacoes_para_uso += conteudo
            elif titulo.startswith("COMO ESTE MEDICAMENTO FUNCIONA"):
                funcionamento_medicamento += conteudo
            elif titulo.startswith("QUANDO NÃO DEVO USAR ESTE MEDICAMENTO"):
                quando_nao_usar += conteudo
            elif titulo.startswith("O QUE DEVO SABER ANTES DE USAR"):
                conhecimento_previo_necessario += conteudo
            elif titulo.startswith("COMO DEVO USAR"):
                como_usar_medicamento += conteudo
            elif titulo.startswith("O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR"):
                esqueceu_medicamento += conteudo
            elif titulo.startswith("QUAIS OS MALES"):
                efeitos_colaterais += conteudo
            elif titulo.startswith("O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR"):
                quantidade_a_mais += conteudo
            elif titulo.startswith("ONDE COMO E POR QUANTO TEMPO POSSO GUARDAR"):
                como_guardar_medicamento += conteudo

print(f"indicacoes_para_uso = {indicacoes_para_uso}")
