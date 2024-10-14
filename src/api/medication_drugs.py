from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from db.manager import Database
from api.schemas.models import *
from api.schemas.schemas import *
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
            select(ComercialNames)
            .options(
                selectinload(ComercialNames.active_principles),
                selectinload(ComercialNames.presentations),
                selectinload(ComercialNames.comercial_names)
            )
            .join(DrugUse)
            .where(DrugUse.user_id == user_id)
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
        drugs = session.exec(select(ComercialNames)
                             .options(selectinload(ComercialNames.active_principles))
                             .options(selectinload(ComercialNames.comercial_names))
                             .options(selectinload(ComercialNames.presentations))
                             ).all()
    return drugs

# Get one drug
@drugs_router.get("/drugs/{{drug_id}}", response_model=DrugRead)
def get_one_drug(drug_id: int):
    with Session(Database.db_engine()) as session:
        drug = session.get(ComercialNames, drug_id, options=[selectinload(ComercialNames.active_principles),
                                                    selectinload(ComercialNames.comercial_names),
                                                    selectinload(ComercialNames.presentations)])
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        return drug