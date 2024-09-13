from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from schema.wounds.schema import TrackingRecords
from schema.wounds.schema import TrackingRecordsPublic
from schema.wounds.schema import TrackingRecordsCreate
from schema.wounds.schema import TrackingRecordsUpdate
from db.manager import Database

wounds_tracking_records_router = APIRouter()
BASE_URL_TRACKING_RECORDS = "/tracking-records/"

@wounds_tracking_records_router.post(BASE_URL_TRACKING_RECORDS, response_model=TrackingRecordsPublic)
def create_tracking_record(
        *,
        session: Session = Depends(Database.get_session),
        tracking_record: TrackingRecordsCreate
):
    """Create a new tracking record"""
    dates = {"created_at": datetime.now(), "updated_at": datetime.now()}
    db_tracking_record = TrackingRecords.model_validate(tracking_record, update=dates)
    session.add(db_tracking_record)
    session.commit()
    session.refresh(db_tracking_record)
    return db_tracking_record

@wounds_tracking_records_router.patch(BASE_URL_TRACKING_RECORDS + "{tracking_record_id}", response_model=TrackingRecordsPublic)
def update_tracking_record(
        *,
        session: Session = Depends(Database.get_session),
        tracking_record_id: int,
        tracking_record: TrackingRecordsUpdate
):
    """Update tracking record"""
    db_tracking_record = session.get(TrackingRecords, tracking_record_id)
    if not db_tracking_record:
        raise HTTPException(status_code=404, detail="Tracking record not found")
    tracking_record_data = db_tracking_record.model_dump(exclude_unset=True)
    updated_at = {"updated_at": datetime.now()}
    db_tracking_record.sqlmodel_update(tracking_record_data, update=updated_at)
    session.add(db_tracking_record)
    session.commit()
    session.refresh(db_tracking_record)
    return db_tracking_record

@wounds_tracking_records_router.get(BASE_URL_TRACKING_RECORDS + "{tracking_record_id}", response_model=TrackingRecordsPublic)
def get_tracking_record_by_id(
        *,
        session: Session = Depends(Database.get_session),
        tracking_record_id: int
):
    """Get specific tracking record"""
    tracking_record = session.get(TrackingRecords, tracking_record_id)
    if not tracking_record:
        raise HTTPException(status_code=404, detail="Tracking record not found")
    return tracking_record

@wounds_tracking_records_router.delete(BASE_URL_TRACKING_RECORDS + "{tracking_record_id}")
def delete_tracking_record(
        *,
        session: Session = Depends(Database.get_session),
        tracking_record_id: int
):
    """Delete tracking record"""
    tracking_record = session.get(TrackingRecords, tracking_record_id)
    if not tracking_record:
        raise HTTPException(status_code=404, detail="Tracking record not found")
    session.delete(tracking_record)
    session.commit()
    return {"ok": True}