from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import os
# Create your views here.

def buscar_medicamento(nome):

    Base_dir = os. path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_path = os.path.join(Base_dir, "api","src","anvisa_data", "anvisa_data.json")

    with open(main_path,  "r", encoding= "utf-8") as f:
        datas = json.load(f)
    
    results = []

    for med in datas["data"]:
        product_name = med[1]

        if nome.lower() in product_name.lower():
            if med[9] == "VÁLIDO":
                results.append({
                    "name": med[1],
                    "register": med[4],
                    "company": med[8],
                    "class": med[7],
                    "active_ingridient": med[10],

            })
    
    
    #informaçoes extras do remedio
    path_ext = os.path.join(Base_dir, "api","src","anvisa_data", "Bulario_data_teste.json")
    with open(path_ext,  "r", encoding= "utf-8") as f:
        data_ext = json.load(f)
        for med in results:
            code = med["registro"]
            if code in data_ext:
               return results
            

            
    if len(results) == 0:
        print(" Medication not found")
        return []
    
    return results

        

def search_med(request):
    name = request.GET.get("nome")
    result = []

    if name:
        result = buscar_medicamento(name)

    return render(request, "medication/search_results.html", {
        "results": result,
        "name": name
    })