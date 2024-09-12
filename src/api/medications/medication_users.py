from datetime import date, datetime
from fastapi import APIRouter, HTTPException
from sqlmodel import Field, SQLModel, Session, select
from schema.medications.medication_users import MeidcationUser
from db.manager import Database

router = APIRouter()

@router.post("/medication/create_user")
def create_user(user: MeidcationUser):
    """Create a new user"""
    with Session(Database.db_engine()) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@router.get("/medication/read_all_users")
def read_all_users():
    """Read all users"""
    with Session(Database.db_engine()) as session:
        users = session.exec(select(MeidcationUser)).all()
        return users

@router.get("/medication/read_one_user")
def read_one_user(user_id):
    """Read one user"""
    with Session(Database.db_engine()) as session:
        user = session.exec(select(MeidcationUser).where(MeidcationUser.id == user_id))
        return user
    
@router.put("/medication/update_user")
def update_user(user_id, user: MeidcationUser):
    """Update a user"""
    with Session(Database.db_engine()) as session:
        user = session.exec(select(MeidcationUser).where(MeidcationUser.id == user_id))
        user.name = user.name
        user.email = user.email
        user.birthday = user.birthday
        user.phone_number = user.phone_number
        user.emergency_contact_name = user.emergency_contact_name
        user.emergency_contact_number = user.emergency_contact_number
        user.accept_tcle = user.accept_tcle
        session.commit()
        session.refresh(user)
        return user
    
@router.delete("/medication/delete_user")
def delete_user(user_id):
    """Delete a user"""
    with Session(Database.db_engine()) as session:
        user = session.exec(select(MeidcationUser).where(MeidcationUser.id == user_id))
        session.delete(user)
        session.commit()
        return user