from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Field, SQLModel, Session, select
from db.manager import Database
from api.schemas.user_schema import User

BASE_URL_USERS = "/medications/user"
user_router = APIRouter()

@user_router.post(BASE_URL_USERS)
def create_user(user: User):
    with Session(Database.db_engine()) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

@user_router.get(BASE_URL_USERS, response_model=list[User])
def read_users():
    with Session(Database.db_engine()) as session:
        users = session.exec(select(User)).all()
    return users

@user_router.get(f"{BASE_URL_USERS}/{{user_id}}", response_model=User)
def read_user(user_id: int):
    with Session(Database.db_engine()) as session:
        user = session.get(User, user_id)
    return user

@user_router.put(f"{BASE_URL_USERS}/{{user_id}}")
def update_user(user_id: int, user: User):
    with Session(Database.db_engine()) as session:
        user_db = session.get(User, user_id)
        if user_db is None:
            raise HTTPException(status_code=404, detail="User not found")
        user_db.name = user.name
        user_db.email = user.email
        user_db.birth_date = user.birth_date
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
    return user_db

@user_router.delete(f"{BASE_URL_USERS}/{{user_id}}")
def delete_user(user_id: int):
    with Session(Database.db_engine()) as session:
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user)
        session.commit()
    return {"message": "User deleted successfully"}
