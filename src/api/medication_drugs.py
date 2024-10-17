from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from db.manager import Database
from api.schemas.models import *
from api.schemas.schemas import *
from typing import List
from sqlalchemy.orm import joinedload

drugs_router = APIRouter()

@drugs_router.get("/user/{user_id}/drugs", response_model=List[DrugRead])
def get_user_drugs(user_id: int):
    with Session(Database.db_engine()) as session:
        # Check if the user exists
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Query to get the user's drug use information
        query = (
            select(DrugUse)
            .options(
                selectinload(DrugUse.comercial_name)
                .selectinload(ComercialNames.active_principles),
                selectinload(DrugUse.comercial_name)
                .selectinload(ComercialNames.presentations)
            )
            .where(DrugUse.user_id == user_id)
        )

        result = session.exec(query)
        drug_uses = result.all()

        if not drug_uses:
            return []

        # Format the result for response
        response = []
        for drug_use in drug_uses:
            drug_data = DrugRead(
                start_date=drug_use.start_date,
                end_date=drug_use.end_date,
                start_time=drug_use.start_time,
                frequency=drug_use.frequency,
                quantity=drug_use.quantity,
                comercial_names=[
                    ComercialNameModel(
                        comercial_name=drug_use.comercial_name.comercial_name,
                        active_principles=[
                            ActivePrincipleModel(
                                code=ap.code,
                                active_ingredient=ap.active_ingredient
                            ) for ap in drug_use.comercial_name.active_principles
                        ],
                        presentations=[
                            PresentationModel(value=pres.value)
                            for pres in drug_use.comercial_name.presentations
                        ]
                    )
                ]
            )
            response.append(drug_data)

        return response

# Get all drugs
@drugs_router.get("/drugs", response_model=List[DrugRead])
def get_all_drugs():
    with Session(Database.db_engine()) as session:
        # Query to get all drugs and their related data through DrugUse
        query = (
            select(DrugUse)
            .options(
                selectinload(DrugUse.comercial_name)
                .selectinload(ComercialNames.active_principles),
                selectinload(DrugUse.presentation)
            )
        )
        drug_uses = session.exec(query).all()

        if not drug_uses:
            return []

        # Format the result for response
        response = []
        for drug_use in drug_uses:
            drug_data = DrugRead(
                start_date=drug_use.start_date,
                end_date=drug_use.end_date,
                start_time=drug_use.start_time,
                frequency=drug_use.frequency,
                quantity=drug_use.quantity,
                comercial_names=[
                    ComercialNameModel(
                        comercial_name=drug_use.comercial_name.comercial_name,
                        active_principles=[
                            ActivePrincipleModel(
                                code=ap.code,
                                active_ingredient=ap.active_ingredient
                            ) for ap in drug_use.comercial_name.active_principles
                        ],
                        presentations=[
                            PresentationModel(value=drug_use.presentation.value)
                        ]
                    )
                ]
            )
            response.append(drug_data)

        return response


# Get one drug
@drugs_router.get("/drugs/{drug_id}", response_model=DrugRead)
def get_one_drug(drug_id: int):
    with Session(Database.db_engine()) as session:
        # Query to get the drug by its ID via DrugUse
        drug_use = session.get(
            DrugUse,
            drug_id,
            options=[
                selectinload(DrugUse.comercial_name)
                .selectinload(ComercialNames.active_principles),
                selectinload(DrugUse.presentation)
            ]
        )

        if not drug_use:
            raise HTTPException(status_code=404, detail="Drug not found")

        # Format the result for response
        drug_data = DrugRead(
            start_date=drug_use.start_date,
            end_date=drug_use.end_date,
            start_time=drug_use.start_time,
            frequency=drug_use.frequency,
            quantity=drug_use.quantity,
            comercial_names=[
                ComercialNameModel(
                    comercial_name=drug_use.comercial_name.comercial_name,
                    active_principles=[
                        ActivePrincipleModel(
                            code=ap.code,
                            active_ingredient=ap.active_ingredient
                        ) for ap in drug_use.comercial_name.active_principles
                    ],
                    presentations=[
                        PresentationModel(value=drug_use.presentation.value)
                    ]
                )
            ]
        )

        return drug_data