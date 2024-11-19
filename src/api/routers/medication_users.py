from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from db.manager import Database
from db.models import User, UserDisease
from api.schemas import *
from sqlalchemy.orm import selectinload

BASE_URL_USERS = "/user"
user_router = APIRouter()

@user_router.post(BASE_URL_USERS, response_model=UserPublic)
def create_user(user: UserCreate):
    with Session(Database.db_engine()) as session:
        new_user = User.model_validate(user)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    return new_user

@user_router.get(BASE_URL_USERS, response_model=list[UserRead])
def read_users():
    with Session(Database.db_engine()) as session:
        users = session.exec(
            select(User)
            .options(selectinload(User.caretakers))
            .options(selectinload(User.disease_links))
        ).all()
    return users

@user_router.get(f"{BASE_URL_USERS}/{{user_id}}", response_model=UserRead)
def read_user(user_id: int):
    with Session(Database.db_engine()) as session:
        user = session.get(
            User, user_id,
            options=[
                selectinload(User.caretakers),
                selectinload(User.disease_links)
            ]
        )
    return user

@user_router.put(f"{BASE_URL_USERS}/{{user_id}}", response_model=UserPublic)
def update_user(user_id: int, user: UserUpdate):
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