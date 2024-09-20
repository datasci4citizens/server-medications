from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Field, SQLModel, Session, select
from src.schema.schema import UserBase
from src.schema.schema import UserCreate
from src.schema.schema import UserUpdate
from src.schema.schema import UserPublic
from src.schema.schema import Users
from db.manager import Database

BASE_URL_USERS = "/medication/user"
medications_user_router = APIRouter()

@medications_user_router.post(BASE_URL_USERS)
def create_user(
    *,
    session: Session = Depends(Database.get_session),
    user: UserCreate
):
    """Create a new user"""
    dates = {"created_at": datetime.now(), "updated_at": datetime.now()}
    db_user = Users.model_validate(user, update=dates)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return user

@medications_user_router.get(BASE_URL_USERS + "{user_id}", response_model=UserPublic)
def get_user_by_id(
        *,
        session: Session = Depends(Database.get_session),
        user_id: int
):
    """Get specific patient"""
    user = session.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@medications_user_router.patch(BASE_URL_USERS + "{user_id}", response_model=UserPublic)
def update_user(
        *,
        session: Session = Depends(Database.get_session),
        patient_id: int,
        patient: UserUpdate
):
    """Update User"""
    db_user = session.get(Users, patient_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    patient_data = patient.model_dump(exclude_unset=True)
    updated_at = {"updated_at": datetime.now()}
    db_user.sqlmodel_update(patient_data, update=updated_at)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user