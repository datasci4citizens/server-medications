from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from db.manager import Database
from api.schemas.models import Drug, User, UserDrugTracking
from api.schemas.schemas import DrugRead
from typing import List
from sqlalchemy.orm import joinedload

drugs_router = APIRouter()

# Get all drugs linked to a specific user
@drugs_router.get("/user/{user_id}/drugs", response_model=List[DrugRead])
def get_user_drugs(user_id: int):
    with Session(Database.db_engine()) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        query = (
            select(Drug)
            .options(
                selectinload(Drug.active_ingredients),
                selectinload(Drug.presentations),
                selectinload(Drug.comercial_names)
            )
            .join(UserDrugTracking)
            .where(UserDrugTracking.user_id == user_id)
        )

        result = session.exec(query)
        drugs = result.all()

        if not drugs:
            return []
        
        return drugs

# Get all drugs
@drugs_router.get("/drugs", response_model=list[DrugRead])
def get_all_drugs():
    with Session(Database.db_engine()) as session:
        drugs = session.exec(select(Drug)
                             .options(selectinload(Drug.active_ingredients))
                             .options(selectinload(Drug.comercial_names))
                             .options(selectinload(Drug.presentations))
                             ).all()
    return drugs

# Get one drug
@drugs_router.get("/drugs/{{drug_id}}", response_model=DrugRead)
def get_one_drug(drug_id: int):
    with Session(Database.db_engine()) as session:
        drug = session.get(Drug, drug_id, options=[selectinload(Drug.active_ingredients),
                                                    selectinload(Drug.comercial_names),
                                                    selectinload(Drug.presentations)])
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        return drug