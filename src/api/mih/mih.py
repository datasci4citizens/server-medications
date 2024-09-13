from datetime import date, datetime
from fastapi import APIRouter, HTTPException
from sqlmodel import Field, SQLModel, Session, select
from schema.medications.medication_users import MihUser
from db.manager import Database

router = APIRouter()

@router.post("/mih/create_user")
def create_user(user: MihUser):
    """Create a new user"""
    with Session(Database.db_engine()) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@router.get("/mih/read_all_users")
def read_all_users():
    """Read all users"""
    with Session(Database.db_engine()) as session:
        users = session.exec(select(MihUser)).all()
        return users

@router.get("/mih/read_one_user")
def read_one_user(user_id):
    """Read one user"""
    with Session(Database.db_engine()) as session:
        user = session.exec(select(MihUser).where(MihUser.id == user_id))
        return user
    
@router.put("/mih/update_user")
def update_user(user_id, user: MihUser):
    """Update a user"""
    with Session(Database.db_engine()) as session:
        user = session.exec(select(MihUser).where(MihUser.id == user_id))
        user.name = user.name
        user.email = user.email
        user.birthday = user.birthday
        user.phone_number = user.phone_number
        session.commit()
        session.refresh(user)
        return user
    
@router.delete("/mih/delete_user")
def delete_user(user_id):
    """Delete a user"""
    with Session(Database.db_engine()) as session:
        user = session.exec(select(MihUser).where(MihUser.id == user_id))
        session.delete(user)
        session.commit()
        return user