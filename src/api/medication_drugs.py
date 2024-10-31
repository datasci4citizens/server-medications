from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from db.manager import Database
from api.schemas.models import *
from api.schemas.schemas import *
from typing import List
from sqlalchemy.orm import joinedload

drugs_router = APIRouter()

@drugs_router.get("/user_drugs/{user_id}/", response_model=List[DrugUseRead])
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
@drugs_router.get("/drugs/", response_model=List[ComercialNameReadWithPresentations])
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
@drugs_router.get("/drugs/{drug_id}", response_model=ComercialNameReadWithPresentations)
def get_one_drug(drug_id: int):
    with Session(Database.db_engine()) as session:
        drug = session.exec(
            select(ComercialNames)
            .where(ActivePrinciple.id == drug_id)
            .options(
                selectinload(ComercialNames.active_principles),
                selectinload(ComercialNames.presentations)
            )).first()

        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        return drug
    
#route to link a user to a new medication 
@drugs_router.post("/user_drugs/{user_id}/", response_model=DrugUseRead)
def link_user_drug(user_id: int, drug: DrugUseCreate):
    with Session(Database.db_engine()) as session:
        # Check if the drug exists
        comercial_name = session.exec(select(ComercialNames).where(ComercialNames.id == drug.comercial_name_id)).first()
        if not comercial_name:
            raise HTTPException(status_code=404, detail="Comercial name not found")
        
        # Check if the presentation exists
        presentation = session.exec(select(Presentations).where(Presentations.id == drug.presentation_id)).first()
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        
        # Check if the user exists
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create the DrugUse object
        drug_use = DrugUse(
            user_id=user_id,
            comercial_name_id=drug.comercial_name_id,
            presentation_id=drug.presentation_id,
            start_date=drug.start_date,
            end_date=drug.end_date,
            observation=drug.observation,
            quantity=drug.quantity
        )

        # Add the drug to the session
        session.add(drug_use)
        session.commit()
        session.refresh(drug_use)

        drug_use = session.exec(
            select(DrugUse)
            .where(DrugUse.id == drug_use.id)
            .options(
                selectinload(DrugUse.comercial_name)
                    .selectinload(ComercialNames.active_principles),
                selectinload(DrugUse.comercial_name)
                    .selectinload(ComercialNames.presentations),
                selectinload(DrugUse.presentation)
            )
        ).first()

        return drug_use
    
#route to return the schedule of a user (just the comercial names, doses and quantities for everfy drug)
@drugs_router.get("/user_drugs/{user_id}/schedule", response_model=List[DrugUseRead])
def get_user_schedule(user_id: int):
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