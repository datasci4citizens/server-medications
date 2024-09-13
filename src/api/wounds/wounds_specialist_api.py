from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from schema.wounds.schema import Specialists
from schema.wounds.schema import SpecialistsPublic
from schema.wounds.schema import SpecialistsCreate
from schema.wounds.schema import SpecialistsUpdate
from db.manager import Database

wounds_specialist_router = APIRouter()
BASE_URL_SPECIALISTS = "/specialists/"

@wounds_specialist_router.post(BASE_URL_SPECIALISTS, response_model=SpecialistsPublic)
def create_specialist(
        *,
        session: Session = Depends(Database.get_session),
        specialist: SpecialistsCreate
):
    """Create a new specialist"""
    dates = {"created_at": datetime.now(), "updated_at": datetime.now()}
    db_specialist = Specialists.model_validate(specialist, update=dates)
    session.add(db_specialist)
    session.commit()
    session.refresh(db_specialist)
    return db_specialist
    

@wounds_specialist_router.patch(BASE_URL_SPECIALISTS + "{specialist_id}", response_model=SpecialistsPublic)
def update_specialist(
        *,
        session: Session = Depends(Database.get_session),
        specialist_id: int,
        specialist: SpecialistsUpdate
):
    """Update specialist"""
    specialist_db = session.get(Specialists, specialist_id)
    if not specialist_db:
        raise HTTPException(status_code=404, detail="Specialist not found")
    specialist_data = specialist.model_dump(exclude_unset=True)
    updated_at = {"updated_at": datetime.now()}
    specialist_db.sqlmodel_update(specialist_data, update=updated_at)
    session.add(specialist_db)
    session.commit()
    session.refresh(specialist_db)
    return specialist_db


@wounds_specialist_router.get(BASE_URL_SPECIALISTS + "{specialist_id}", response_model=SpecialistsPublic)
def get_specialist_by_id(
        *,
        session: Session = Depends(Database.get_session),
        specialist_id: int
):
    """Get specific specialist"""
    specialist = session.get(Specialists, specialist_id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    return specialist

@wounds_specialist_router.get(BASE_URL_SPECIALISTS, response_model=list[SpecialistsPublic])
def get_all_specialists(
        *,
        session: Session = Depends(Database.get_session),
        offset: int = 0,
        limit: int = Query(default=100, le=100)
):
    """Get all specialists"""
    specialists = session.exec(select(Specialists).offset(offset).limit(limit)).all()
    return specialists

@wounds_specialist_router.delete(BASE_URL_SPECIALISTS + "{specialist_id}")
def delete_specialist(
        *,
        session: Session = Depends(Database.get_session),
        specialist_id: int
):
    """Delete specialist"""
    specialist = session.get(Specialists, specialist_id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    session.delete(specialist)
    session.commit()
    return {"ok": True}