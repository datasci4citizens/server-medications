from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session
from schema.wounds.schema import Wounds
from schema.wounds.schema import WoundsPublic
from schema.wounds.schema import WoundsCreate
from schema.wounds.schema import WoundsUpdate
from schema.wounds.schema import WoundsPublicWithPatient
from schema.wounds.schema import WoundsPublicWithTrackingRecords
from schema.wounds.schema import WoundsPublicWithWoundType
from db.manager import Database

wounds_router = APIRouter()
BASE_URL_WOUNDS = "/wounds/"

@wounds_router.post(BASE_URL_WOUNDS, response_model=WoundsPublic)
def create_wound(
        *,
        session: Session = Depends(Database.get_session),
        wound: WoundsCreate
):
    """Create a new wound"""
    dates = {"created_at": datetime.now(), "updated_at": datetime.now()}
    if wound.start_date == None:
        dates.update({"start_date": datetime.now})
    db_wound = Wounds.model_validate(wound, update=dates)
    session.add(db_wound)
    session.commit()
    session.refresh(db_wound)
    return db_wound

@wounds_router.patch(BASE_URL_WOUNDS + "{wound_id}", response_model=WoundsPublic)
def update_wound(
        *,
        session: Session = Depends(Database.get_session),
        wound_id: int,
        wound: WoundsUpdate
):
    """Update wound end date"""
    db_wound = session.get(Wounds, wound_id)
    if not db_wound:
        raise HTTPException(status_code=404, detail="Wound not found")
    wound_data = db_wound.model_dump(exclude_unset=True)
    updated_at = {"updated_at": datetime.now()}
    db_wound.sqlmodel_update(wound_data, update=updated_at)
    session.add(db_wound)
    session.commit()
    session.refresh(db_wound)
    return db_wound

@wounds_router.get(BASE_URL_WOUNDS + "{wound_id}", response_model=WoundsPublicWithWoundType)
def get_wound_by_id(
        *,
        session: Session = Depends(Database.get_session),
        wound_id: int
):
    """Get specific wound"""
    wound = session.get(Wounds, wound_id)
    if not wound:
        raise HTTPException(status_code=404, detail="Wound not found")
    return wound

@wounds_router.get(BASE_URL_WOUNDS + "{wound_id}" + "/patient", response_model=WoundsPublicWithPatient)
def get_wound_with_patient(
        *,
        session: Session = Depends(Database.get_session),
        wound_id: int
):
    """Get specific wound"""
    wound = session.get(Wounds, wound_id)
    if not wound:
        raise HTTPException(status_code=404, detail="Wound not found")
    return wound

@wounds_router.get(BASE_URL_WOUNDS + "{wound_id}" + "/tracking-records", response_model=WoundsPublicWithTrackingRecords)
def get_wound_tracking_records(
        *,
        session: Session = Depends(Database.get_session),
        offset: int = 0,
        limit: int = Query(default=100, le=100),
        wound_id: int
):
    """Get all tracking records from wound"""
    wound = session.get(Wounds, wound_id)
    if not wound:
        raise HTTPException(status_code=404, detail="Wound not found")
    return wound

@wounds_router.delete(BASE_URL_WOUNDS + "{wound_id}")
def delete_wound(
        *,
        session: Session = Depends(Database.get_session),
        wound_id: int
):
    """Delete wound"""
    wound = session.get(Wounds, wound_id)
    if not wound:
        raise HTTPException(status_code=404, detail="Wound not found")
    session.delete(wound)
    session.commit()
    return {"ok": True}