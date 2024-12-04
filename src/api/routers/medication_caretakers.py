from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session, select
from db.manager import Database
from db.models import User, UserCaretaker
from api.schemas import *
from sqlalchemy.orm import selectinload
from auth.auth_service import AuthService

BASE_URL_CARETAKERS = "/caretaker"
caretaker_router = APIRouter(dependencies=[Depends(AuthService.get_current_user)])

@caretaker_router.get(BASE_URL_CARETAKERS, response_model=list[UserPublic])
def read_caretakers():
    with Session(Database.db_engine()) as session:
        caretakers = session.exec(
            select(User).where(User.is_caretaker == True)
        ).all()
    return caretakers
    
@caretaker_router.get(f"{BASE_URL_CARETAKERS}/relationships")
def get_user_relationships(request: Request):
    with Session(Database.db_engine()) as session:
        user_id = request.session.get("id")
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Fetch caretakers and users cared for
        caretakers = session.exec(
            select(User).join(UserCaretaker, User.id == UserCaretaker.caretaker_id).where(
                UserCaretaker.user_id == user_id
            )
        ).all()
        users_cared_for = session.exec(
            select(User).join(UserCaretaker, User.id == UserCaretaker.user_id).where(
                UserCaretaker.caretaker_id == user_id
            )
        ).all()

        return {
            "user_id": user_id,
            "caretakers": [{"id": c.id, "name": c.name} for c in caretakers],
            "users_cared_for": [{"id": u.id, "name": u.name} for u in users_cared_for],
        }
    
@caretaker_router.post(f"{BASE_URL_CARETAKERS}/caretakers/{{caretaker_id}}")
def link_user_and_caretaker(request: Request, caretaker_id: int):
    with Session(Database.db_engine()) as session:
        user_id = request.session.get("id")
        # Fetch users to ensure they exist
        user = session.get(User, user_id)
        caretaker = session.get(User, caretaker_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not caretaker or not caretaker.is_caretaker:
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
        user_caretaker = UserCaretaker(user_id=user.id, caretaker_id=caretaker.id)
        session.add(user_caretaker)
        session.commit()

    return {"message": "Caretaker linked to user successfully"}