from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from db.manager import Database
from api.schemas.models import Drug, UserUseDrug, User

relationships_router = APIRouter()

# Get all drugs linked to a specific patient (user)
@relationships_router.get(f"/user/{{user_id}}/drugs", response_model=User)
def get_user_drugs(user_id: int):
    with Session(Database.db_engine()) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.drugs

# Get all drugs
@relationships_router.get("/drugs", response_model=list[Drug])
def get_all_drugs():
    with Session(Database.db_engine()) as session:
        drugs = session.exec(select(Drug)).all()
    return drugs

# Get one drug
@relationships_router.get("/drugs/{{drug_id}}", response_model=Drug)
def get_one_drug(drug_id: int):
    with Session(Database.db_engine()) as session:
        drug = session.get(Drug, drug_id)
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        return drug