from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from db.manager import Database
from api.schemas.models import *
from api.schemas.schemas import *
from typing import List
from sqlalchemy.orm import joinedload

drugs_router = APIRouter()

@drugs_router.get("/users/{user_id}/drugs", response_model=List[DrugUseRead])
def get_user_drugs(user_id: int):
    # Query the DrugUse table to get all drug uses for the given user
    with Session(Database.db_engine()) as session:
        user_drugs = session.exec(
            select(DrugUse)
            .where(DrugUse.user_id == user_id)
            .options(
                selectinload(DrugUse.comercial_name).selectinload(ComercialNames.presentations),
                selectinload(DrugUse.comercial_name).selectinload(ComercialNames.active_principles),  # Load active principles
                selectinload(DrugUse.presentation)  # Load the specific presentation
            )
        ).all()

        if not user_drugs:
            raise HTTPException(status_code=404, detail="No drugs found for this user")

        return user_drugs

# Route to fetch all drugs
@drugs_router.get("/drugs/", response_model=List[ComercialNameRead])
def get_all_drugs():
    with Session(Database.db_engine()) as session:
        drugs = session.exec(
            select(ComercialNames).options(
                selectinload(ComercialNames.active_principles),
                selectinload(ComercialNames.presentations)
            )
                ).all()
        return drugs

# Route to fetch a specific drug by id
@drugs_router.get("/drugs/{drug_id}", response_model=DrugReadWithDetails)
def get_one_drug(drug_id: int):
    with Session(Database.db_engine()) as session:
        drug = session.exec(
            select(ActivePrinciple)
            .where(ActivePrinciple.id == drug_id)
            .options(
                selectinload(ActivePrinciple.comercial_names)#.selectinload(ComercialNames.presentations)
            )
        ).first()

        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        return drug