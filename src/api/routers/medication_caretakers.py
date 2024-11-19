from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from db.manager import Database
from db.models import Caretaker, User, UserCaretaker
from api.schemas import *
from sqlalchemy.orm import selectinload

BASE_URL_CARETAKERS = "/caretaker"
caretaker_router = APIRouter()

@caretaker_router.post(BASE_URL_CARETAKERS, response_model=CaretakerPublic)
def create_caretaker(caretaker: CaretakerCreate):
    with Session(Database.db_engine()) as session:
        new_caretaker = Caretaker.model_validate(caretaker)
        session.add(new_caretaker)
        session.commit()
        session.refresh(new_caretaker)
    return new_caretaker

@caretaker_router.get(BASE_URL_CARETAKERS, response_model=list[CaretakerPublic])
def read_caretakers():
    with Session(Database.db_engine()) as session:
        caretakers = session.exec(
            select(Caretaker)
            .options(selectinload(Caretaker.users))
        ).all()
    return caretakers

@caretaker_router.get(f"{BASE_URL_CARETAKERS}/{{caretaker_id}}", response_model=CaretakerPublic)
def read_caretaker(caretaker_id: int):
    with Session(Database.db_engine()) as session:
        caretaker = session.get(
            Caretaker, caretaker_id,
            options=[selectinload(Caretaker.users)]
        )
        if caretaker is None:
            raise HTTPException(status_code=404, detail="Caretaker not found")
    return caretaker

@caretaker_router.put(f"{BASE_URL_CARETAKERS}/{{caretaker_id}}", response_model=CaretakerPublic)
def update_caretaker(caretaker_id: int, caretaker: CaretakerUpdate):
    with Session(Database.db_engine()) as session:
        caretaker_db = session.get(Caretaker, caretaker_id)
        if caretaker_db is None:
            raise HTTPException(status_code=404, detail="Caretaker not found")
        caretaker_data = caretaker.dict(exclude_unset=True)
        for key, value in caretaker_data.items():
            setattr(caretaker_db, key, value)
        session.add(caretaker_db)
        session.commit()
        session.refresh(caretaker_db)
    return caretaker_db

@caretaker_router.delete(f"{BASE_URL_CARETAKERS}/{{caretaker_id}}")
def delete_caretaker(caretaker_id: int):
    with Session(Database.db_engine()) as session:
        caretaker = session.get(Caretaker, caretaker_id)
        if caretaker is None:
            raise HTTPException(status_code=404, detail="Caretaker not found")
        session.delete(caretaker)
        session.commit()
    return {"message": "Caretaker deleted successfully"}

@caretaker_router.get(f"{BASE_URL_CARETAKERS}/{{user_id}}/caretakers", response_model=list[CaretakerPublic])
def read_caretakers_for_user(user_id: int):
    with Session(Database.db_engine()) as session:
        user = session.exec(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.caretakers))
        ).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user.caretakers
    
@caretaker_router.post(f"{BASE_URL_CARETAKERS}/{{user_id}}/caretakers/{{caretaker_id}}")
def link_user_and_caretaker(user_id: int, caretaker_id: int):
    with Session(Database.db_engine()) as session:
        # Fetch user and caretaker to ensure they exist
        user = session.get(User, user_id)
        caretaker = session.get(Caretaker, caretaker_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not caretaker:
            raise HTTPException(status_code=404, detail="Caretaker not found")

        # Check if the link already exists
        existing_link = session.exec(
            select(UserCaretaker).where(
                UserCaretaker.user_id == user_id,
                UserCaretaker.caretaker_id == caretaker_id
            )
        ).first()

        if existing_link:
            raise HTTPException(status_code=400, detail="User and caretaker are already linked")

        # Create the link
        user_caretaker = UserCaretaker(user_id=user_id, caretaker_id=caretaker_id)
        session.add(user_caretaker)
        session.commit()

    return {"message": "Caretaker linked to user successfully"}