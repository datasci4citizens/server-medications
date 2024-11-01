from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from db.manager import Database
from api.schemas.models import Disease, User, UserDisease
from api.schemas.schemas import DiseaseCreate, DiseaseUpdate, DiseaseRead, DiseasePublic, UserDiseaseModel, DiseaseModel

BASE_URL_DISEASES = "/diseases"
disease_router = APIRouter()

@disease_router.post(BASE_URL_DISEASES, response_model=DiseasePublic)
def create_disease(disease: DiseaseCreate):
    with Session(Database.db_engine()) as session:
        new_disease = Disease(name=disease.name, description=disease.description)
        session.add(new_disease)
        session.commit()
        session.refresh(new_disease)
    return new_disease

@disease_router.get(BASE_URL_DISEASES, response_model=list[DiseaseRead])
def read_diseases():
    with Session(Database.db_engine()) as session:
        diseases = session.exec(select(Disease)).all()
    return diseases

@disease_router.get(f"{BASE_URL_DISEASES}/{{disease_id}}", response_model=DiseaseRead)
def read_disease(disease_id: int):
    with Session(Database.db_engine()) as session:
        disease = session.get(Disease, disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail="Disease not found")
    return disease

@disease_router.put(f"{BASE_URL_DISEASES}/{{disease_id}}", response_model=DiseasePublic)
def update_disease(disease_id: int, disease: DiseaseUpdate):
    with Session(Database.db_engine()) as session:
        existing_disease = session.get(Disease, disease_id)
        if not existing_disease:
            raise HTTPException(status_code=404, detail="Disease not found")
        if disease.name is not None:
            existing_disease.name = disease.name
        if disease.description is not None:
            existing_disease.description = disease.description
        session.add(existing_disease)
        session.commit()
        session.refresh(existing_disease)
    return existing_disease

@disease_router.delete(f"{BASE_URL_DISEASES}/{{disease_id}}")
def delete_disease(disease_id: int):
    with Session(Database.db_engine()) as session:
        disease = session.get(Disease, disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail="Disease not found")
        session.delete(disease)
        session.commit()
    return {"message": "Disease deleted successfully"}

#route to add disease to user
@disease_router.post(f"{BASE_URL_DISEASES}/{{user_id}}/disease/", response_model=UserDiseaseModel)
def add_disease_to_user(user_id: int, disease: DiseaseModel):
    with Session(Database.db_engine()) as session:
        # Check if the user exists
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if the disease link already exists
        existing_link = session.exec(
            select(UserDisease)
            .where(UserDisease.user_id == user_id)
            .where(UserDisease.disease_id == disease.disease_id)
        ).first()
        
        if existing_link:
            raise HTTPException(status_code=400, detail="User is already linked to this disease")
        
        user_disease = UserDisease(
            user_id=user_id,
            disease_id=disease.disease_id,
            status=disease.status
        )
        session.add(user_disease)
        session.commit()
        session.refresh(user_disease)
    return user_disease