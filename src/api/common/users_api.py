from fastapi import APIRouter
from sqlmodel import Session, select
from schema.common.users_schema import Users
from db.manager import Database

router = APIRouter()

@router.post("/users/")
def create_user(user: Users):
    """Create a new user"""
    with Session(Database.db_engine()) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@router.get("/users/")
def read_users():
    """Read all users"""
    with Session(Database.db_engine()) as session:
        users = session.exec(select(Users)).all()
        return users
