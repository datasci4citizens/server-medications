import os
import sys
import pandas as pd
from sqlmodel import Session, select

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from db.manager import Database
from db.models import ActivePrinciple

def add_active_principles():
    # Lê o Excel com os dados
    script_dir = os.path.dirname(__file__)  # Diretório do script atual
    file_path = os.path.join(script_dir, 'lista_principios_ativos_cas.xlsx')
    df = pd.read_excel(file_path)

    with Session(Database.db_engine()) as session:
        for _, row in df.iterrows():
            # Cria instância do ActivePrinciple com os valores do Excel
            active_principle = ActivePrinciple(
                code=row["Nº CAS"],  # Coluna do número CAS
                active_ingredient=row["DENOMINAÇÃO COMUM BRASILEIRA"].rstrip().capitalize()  # Coluna do nome
            )
            session.add(active_principle)

        session.commit()
        print("Dados inseridos com sucesso.")

if __name__ == "__main__":
    add_active_principles()