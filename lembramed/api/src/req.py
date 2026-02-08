from interage.api import InterageAPI
api opensource
#need to get api token
# api = InterageAPI(auth = 'your-api-token')
# medicamentos = api.medicamentos.filter(search = 'acido').objects()

# for m in medicamentos:
#     print(m.nome)

api = InterageAPI(auth = { 'username': 'Bedunado', 'password': '12345678'})

medications = api.medicamentos.all()
pa = api.principios_ativos.all()
i = api.interacoes.all()

#medicamentos = results.objects() # Lista de instâncias da classe Medicamento
medicamentos_json = medications.json() # JSON com lista de medicamentos
pa_json = pa.json()
i_json = i.json()

write_json('medicamentos', medicamentos_json)
write_json('principios_ativos', pa_json)
write_json('interacoes', i_json)

# for m in medicamentos:
#     print(m.nome)
 
# for m in medicamentos_json:
#     print(m['nome'])

def write_json(target_file, data):
    if not os.path.exists(target_path):
        try:
            os.makedirs(target_path)
        except Exeption as e:
            print(e)
            raise
    with open(os.path.join(f"api_data/ + {target_file}.json"), "w") as f:
        json.dump(data,f, indent=4)