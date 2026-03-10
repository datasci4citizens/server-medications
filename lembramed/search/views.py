from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
# Create your views here.

def buscar_medicamento(nome):

    with open("anvisa_data.json", "r", encoding= "utf-8") as f:
        dados = json.load(f)
    
    resultados = []

    for med in dados["data"]:
        nome_produto = med[1]

        if nome.lower() in nome_produto.lower():
            if med[9] == "VÁLIDO":
                resultados.append({
                    "nome": med[1],
                    "registro": med[4],
                    "empresa": med[5],
                    "classe": med[6],
                    "principio_ativo": med[7],

            })
    if len(resultados) == 0:
            print(" Medication not found")
            return 0
        
    return resultados

@api_view(['GET'])
def search_med(request):
    nome = request.GET.get("nome")
    resultado = buscar_medicamento(nome)
    return Response(resultado)