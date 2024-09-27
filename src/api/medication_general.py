from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from db.manager import Database
from api.schemas.models import Drug, UserDrug, DrugInteraction, Food, FoodInteraction

BASE_URL_MEDICATIONS = "/medications"
drug_router = APIRouter()

# 1. Get all drugs linked to a specific patient (user)
@drug_router.get(f"{BASE_URL_MEDICATIONS}/user/{{user_id}}/drugs", response_model=list[Drug])
def get_user_drugs(user_id: int):
    with Session(Database.db_engine()) as session:
        statement = select(Drug).join(UserDrug).where(UserDrug.user_id == user_id)
        drugs = session.exec(statement).all()
        if not drugs:
            raise HTTPException(status_code=404, detail="No drugs found for this user")
        return drugs

# 2. Get all drug interactions linked to a specific drug
@drug_router.get(f"{BASE_URL_MEDICATIONS}/drug/{{drug_id}}/interactions", response_model=list[DrugInteraction])
def get_drug_interactions(drug_id: int):
    with Session(Database.db_engine()) as session:
        statement = select(DrugInteraction).where(DrugInteraction.drug_a_id == drug_id)
        interactions = session.exec(statement).all()
        if not interactions:
            raise HTTPException(status_code=404, detail="No interactions found for this drug")
        return interactions

# 3. Get all foods that interact with a specific drug	
@drug_router.get(f"{BASE_URL_MEDICATIONS}/drug/{{drug_id}}/foods", response_model=list[Food])
def get_drug_foods(drug_id: int):
    with Session(Database.db_engine()) as session:
        statement = select(Food).join(FoodInteraction).where(FoodInteraction.drug_id == drug_id)
        foods = session.exec(statement).all()
        if not foods:
            raise HTTPException(status_code=404, detail="No foods interact with this drug")