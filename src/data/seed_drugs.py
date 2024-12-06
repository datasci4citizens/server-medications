import os
import sys
import pandas as pd
from sqlmodel import Session, select

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.manager import Database
from db.models import ActivePrinciple, ComercialNames, ComercialNamesActivePrinciple, ComercialNamesPresentations, Presentations

form_mapping = {
    "ades": "Adesivo",
    "aer or": "Aerossol oral",
    "anel": "Anel",
    "anel vag": "Anel vaginal",
    "bar": "Barra",
    "bast": "Bastão",
    "bomb": "Bombeador",
    "cap dura com mgran lib retard": "Cápsula dura com microgranulos de liberaçao retardada",
    "cap dura po inal or": "Cápsula dura com pó para inalação",
    "cap dura com mgran": "Cápsula dura com microgranulos",
    "cap dura lib prol": "Cápsula dura de liberação prolongada",
    "cap dura lib retard": "Cápsula dura de liberação retardada",
    "cap mole lib prol": "Cápsula mole de liberação prolongada",
    "cap mole lib retard": "Cápsula mole de liberação retardada",
    "cap acao prol": "Cápsula de ação prolongada",
    "cap dura": "Cápsula dura",
    "cap mole": "Cápsula mole",
    "colut spr": "Colutório spray",
    "colut": "Colutório",
    "com rev lib prol": "Comprimido revestido de liberação prolongada",
    "com rev lib retard": "Comprimido revestido de liberação retardada",
    "com rev gelatinizado": "Comprimido revestido gelatinizado",
    "com lib mod": "Comprimido de liberação modificada",
    "com lib prol": "Comprimido de liberação prolongada",
    "com colut": "Comprimido para colutório",
    "com efev": "Comprimido efervescente",
    "com mast": "Comprimido mastigável",
    "com orodisp": "Comprimido orodispersível",
    "com rev": "Comprimido revestido",
    "com sol": "Comprimido para solução",
    "com sus": "Comprimido para suspensão",
    "com": "Comprimido",
    "crem vag": "Creme vaginal",
    "crem": "Creme",
    "diu": "Dispositivo intra-uterino",
    "disp inal": "Dispositivo inalador",
    "disp or": "Dispositivo oral",
    "drag": "Dragea simples",
    "elx": "Elixir",
    "empl": "Emplasto",
    "emu aer": "Emulsão aerossol",
    "emu got": "Emulsão gotas",
    "emu infus": "Emulsão para infusão",
    "emu inj": "Emulsão injetável",
    "emu spr": "Emulsão spray",
    "emu": "Emulsão",
    "espaç": "Espaçador",
    "esm": "Esmalte",
    "esp": "Espuma",
    "fil": "Filme",
    "gas": "Gás",
    "gel lib prol": "Gel de liberação prolongada",
    "gel": "Gel",
    "glob": "Glóbulo",
    "goma": "Goma de mascar",
    "gran rev lib prol": "Granulado revestido de liberação prolongada",
    "gran rev lib retard": "Granulado revestido de liberação retardada",
    "gran efev": "Granulado efervescente",
    "gran rev": "Granulado revestido",
    "gran sol": "Granulado para solução",
    "gran sus": "Granulado para suspensão",
    "gran": "Granulado",
    "impl": "Implante",
    "liq": "Líquido",
    "loç": "Loção",
    "ole": "Óleo",
    "ovl": "Óvulo",
    "pas dura": "Pastilha dura",
    "pas gom": "Pastilha gomosa",
    "past": "Pasta",
    "po liof sus inj lib prol": "Pó liofilizado para suspensão injetável de liberação prolongada",
    "po sus inj lib prol": "Pó para suspensão injetável de liberação prolongada",
    "po liof sol infus": "Pó liofilizado para solução para infusão",
    "po liof sol inj": "Pó liofilizado para solução injetável",
    "po liof sus inj": "Pó liofilizado para suspensão injetável",
    "po liof inj": "Pó liofilizado injetável",
    "po prep ext": "Pó Para preparo extemporâneo",
    "po sol infus": "Pó para solução para infusão",
    "po sol inj": "Pó para solução injetável",
    "po sus inj": "Pó para suspensão injetável",
    "po sus or": "Pó para suspensão oral",
    "po aer": "Pó aerossol",
    "po colut": "Pó para colutório",
    "po efev": "Pó efervescente",
    "po inal": "Pó inalante",
    "po inj": "Pó injetável",
    "po sol": "Pó para solução",
    "po sus": "Pó para suspensão",
    "po top": "Pó tópico",
    "po": "Pó",
    "pom": "Pomada",
    "ras": "Rasura",
    "sab": "Sabonete",
    "sab liq": "Sabonete líquido",
    "sol dil colut": "Solução para diluição para colutório",
    "sol dil infus": "Solução para diluição para infusão",
    "sol dil inj": "Solução para diluição injetável",
    "sol inal or": "Solução inalatória por via oral",
    "sol lib prol": "Solução de liberação prolongada",
    "sol spr nas": "Solução spray nasal",
    "sol aer": "Solução aerossol",
    "sol capilar": "Solução capilar",
    "sol dil": "Solução para diluição",
    "sol got": "Solução gotas",
    "sol inal": "Solução inalante",
    "sol infus": "Solução para infusão",
    "sol inj": "Solução injetável",
    "sol irr": "Solução para irrigação",
    "sol spr": "Solução spray",
    "sol": "Solução",
    "spr nas": "Spray nasal",
    "sup": "Supositório",
    "sus inj lib prol": "Suspensão injetável de liberação prolongada",
    "sus lib prol": "Suspensão de liberação prolongada",
    "sus lib retard": "Suspensão de liberação retardada",
    "sus aer inal or": "Suspensão aerossol inalatória por via oral",
    "sus got": "Suspensão gotas",
    "sus inal": "Suspensão para nebulização",
    "sus inj": "Suspensão injetável",
    "sus spr": "Suspensão spray",
    "sus": "Suspensão",
    "table": "Tablete",
    "xamp": "Xampu",
    "xpe": "Xarope"
}

# Função para remover quebras de linha e espaços extras
def clean_text(text):
    return text.replace('\n', ' ').strip() if isinstance(text, str) else text

# Função para transformar o campo Associação em lista, com limpeza
def process_active_principles(association):
    if pd.isna(association):
        return []
    ingredients = [clean_text(item).capitalize() for item in association.split('+')]
    return ingredients

# Função para substituir e limpar a Forma Farmacêutica
def process_pharmaceutical_form(form):
    form = form.lower() 
    to_return = ""
    first = True

    for pharmaceutical_form in form.split('+'):
        pharmaceutical_form = clean_text(pharmaceutical_form) 
        matched = False 
        
        if not first:
            to_return += " + "
        first = False
        
        for key, value in form_mapping.items():
            if key in pharmaceutical_form:
                to_return += value
                matched = True
                break 
                
        if not matched:
            to_return += pharmaceutical_form.capitalize() 
    
    return to_return

def add_drugs_from_sheet(file_path):
    df = pd.read_excel(file_path)
    active_principle_column_name = df.columns[0]

    with Session(Database.db_engine()) as session:
        for _, row in df.iterrows():
            id = row["REGISTRO"]
            comercial_name = clean_text(row["MEDICAMENTO"]).capitalize()
            active_principles = process_active_principles(row[active_principle_column_name])
            concentration = clean_text(row["CONCENTRAÇÃO"])
            pharmaceutical_form = process_pharmaceutical_form(row["FORMA FARMACÊUTICA"])

            db_presentation = session.exec(select(Presentations)
                .where(Presentations.concentration == concentration)
                .where(Presentations.pharmaceutical_form == pharmaceutical_form)
            ).first()

            if not db_presentation:
                db_presentation = Presentations(concentration=concentration, pharmaceutical_form=pharmaceutical_form)
                session.add(db_presentation)
                session.commit()
                session.refresh(db_presentation)
        
        
            db_comercial_name = session.exec(select(ComercialNames).where(ComercialNames.id == id)).first()
            if not db_comercial_name:
                db_comercial_name = ComercialNames(id = id, comercial_name = comercial_name)
                session.add(db_comercial_name)
                session.commit()
                session.refresh(db_comercial_name)

                for active_principle in active_principles:
                    print("active_principle:", active_principle, "/ concentration:", db_presentation.concentration, "/ pharmaceutical form:", db_presentation.pharmaceutical_form)
                    db_active_principle = session.exec(select(ActivePrinciple).where(ActivePrinciple.active_ingredient == active_principle)).first()
                    comercial_name_active_principle = ComercialNamesActivePrinciple(active_principle_id = db_active_principle.id, comercial_name_id = db_comercial_name.id)
                    session.add(comercial_name_active_principle)
            
            comercial_name_presentation = ComercialNamesPresentations(comercial_name_id = db_comercial_name.id, presentation_id = db_presentation.id)
            session.add(comercial_name_presentation)

        session.commit()
        print("Dados inseridos com sucesso.")

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__) 
    file_path_associacao = os.path.join(script_dir, 'lista_b_associacao.xlsx')
    file_path_farmaco = os.path.join(script_dir, 'lista_a_farmaco.xlsx')

    add_drugs_from_sheet(file_path_associacao)
    add_drugs_from_sheet(file_path_farmaco)