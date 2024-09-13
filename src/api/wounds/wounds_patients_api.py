from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from schema.wounds.schema import Patients
from schema.wounds.schema import PatientsPublic
from schema.wounds.schema import PatientsCreate
from schema.wounds.schema import PatientsUpdate
from schema.wounds.schema import PatientsPublicWithWounds
from db.manager import Database

wounds_patients_router = APIRouter()
BASE_URL_PATIENTS = "/patients/"


@wounds_patients_router.post(BASE_URL_PATIENTS, response_model=PatientsPublic)
def create_patient(
        *,
        session: Session = Depends(Database.get_session),
        patient: PatientsCreate
):
    """Create a new patient"""
    dates = {"created_at": datetime.now(), "updated_at": datetime.now()}
    db_patient = Patients.model_validate(patient, update=dates)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient


@wounds_patients_router.patch(BASE_URL_PATIENTS + "{patient_id}", response_model=PatientsPublic)
def update_patient(
        *,
        session: Session = Depends(Database.get_session),
        patient_id: int,
        patient: PatientsUpdate
):
    """Update patient"""
    db_patient = session.get(Patients, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient_data = patient.model_dump(exclude_unset=True)
    updated_at = {"updated_at": datetime.now()}
    db_patient.sqlmodel_update(patient_data, update=updated_at)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient


@wounds_patients_router.get(BASE_URL_PATIENTS + "{patient_id}", response_model=PatientsPublic)
def get_patient_by_id(
        *,
        session: Session = Depends(Database.get_session),
        patient_id: int
):
    """Get specific patient"""
    patient = session.get(Patients, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@wounds_patients_router.get(BASE_URL_PATIENTS, response_model=list[PatientsPublic])
def get_all_patients(
        *,
        session: Session = Depends(Database.get_session),
        offset: int = 0,
        limit: int = Query(default=100, le=100)
):
    """Get all patients"""
    patients = session.exec(select(Patients).offset(offset).limit(limit)).all()
    return patients

@wounds_patients_router.get(BASE_URL_PATIENTS + "{patient_id}" + "/wounds", response_model=PatientsPublicWithWounds)
def get_patient_wounds(
        *,
        session: Session = Depends(Database.get_session),
        patient_id: int
):
    patient = session.get(Patients, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

""" ao remover um paciente, eu tenho que remover todas as feridas relacionadas """
@wounds_patients_router.delete(BASE_URL_PATIENTS + "{patient_id}")
def delete_patient(
        *,
        session: Session = Depends(Database.get_session),
        patient_id: int
):
    """Delete patient"""
    patient = session.get(Patients, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    session.delete(patient)
    session.commit()
    return {"ok": True}