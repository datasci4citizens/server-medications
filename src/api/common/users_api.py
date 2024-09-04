from fastapi import APIRouter
from sqlmodel import Session, select
from schema.common.users_schema import Users

router = APIRouter()

@router.post("/users/")
def create_user(user: Users):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@router.get("/users/")
def read_users():
    with Session(engine) as session:
        users = session.exec(select(Users)).all()
        return users
