from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import os
# Create your views here.

def buscar_medicamento(nome):

    Base_dir = os. path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(Base_dir, "api","src","anvisa_data", "anvisa_data.json")

    with open(caminho,  "r", encoding= "utf-8") as f:
        dados = json.load(f)
    
    resultados = []

    for med in dados["data"]:
        nome_produto = med[1]

        if nome.lower() in nome_produto.lower():
            if med[9] == "VÁLIDO":
                resultados.append({
                    "nome": med[1],
                    "registro": med[4],
                    "empresa": med[8],
                    "classe": med[7],
                    "principio_ativo": med[10],

            })
    
    
    #informaçoes extras do remedio
    caminho_ext = os.path.join(Base_dir, "api","src","anvisa_data", "Bulario_data_teste.json")
    with open(caminho_ext,  "r", encoding= "utf-8") as f:
        dados_ext = json.load(f)
        for med in resultados:
            codigo = med["registro"]
            if codigo in dados_ext:
               return resultados
            

            
    if len(resultados) == 0:
        print(" Medication not found")
        return []
    
    return resultados

        

def search_med(request):
    nome = request.GET.get("nome")
    resultado = []

    if nome:
        resultado = buscar_medicamento(nome)

    return render(request, "medication/search_results.html", {
        "resultados": resultado,
        "nome": nome
    })