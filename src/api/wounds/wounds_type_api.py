from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from schema.wounds.schema import WoundTypes
from schema.wounds.schema import WoundTypesPublic
from schema.wounds.schema import WoundTypesCreate
from schema.wounds.schema import WoundTypesUpdate
from db.manager import Database

wounds_type_router = APIRouter()
BASE_URL_WOUNDS_TYPE = "/wounds-type/"

@wounds_type_router.post(BASE_URL_WOUNDS_TYPE, response_model=WoundTypesPublic)
def create_wound_type(
        *,
        session: Session = Depends(Database.get_session),
        wound_type: WoundTypesCreate
):
    """Create a new wound type"""
    dates = {"created_at": datetime.now(), "updated_at": datetime.now()}
    db_wound_type = WoundTypes.model_validate(wound_type, update=dates)
    session.add(db_wound_type)
    session.commit()
    session.refresh(db_wound_type)
    return db_wound_type


@wounds_type_router.patch(BASE_URL_WOUNDS_TYPE + "{wound_type_id}", response_model=WoundTypesPublic)
def update_wound_type(
        *,
        session: Session = Depends(Database.get_session),
        wound_type_id: int,
        wound_type: WoundTypesUpdate
):
    """Update wound type"""
    db_wound_type = session.get(WoundTypes, wound_type_id)
    if not db_wound_type:
        raise HTTPException(status_code=404, detail="Wound type not found")
    wound_type_data = wound_type.model_dump(exclude_unset=True)
    updated_at = {"updated_at": datetime.now()}
    db_wound_type.sqlmodel_update(wound_type_data, update=updated_at)
    session.add(db_wound_type)
    session.commit()
    session.refresh(db_wound_type)
    return db_wound_type


@wounds_type_router.get(BASE_URL_WOUNDS_TYPE + "{wound_type_id}", response_model=WoundTypesPublic)
def get_wound_type_by_id(
        *,
        session: Session = Depends(Database.get_session),
        wound_type_id: int
):
    """Get specific wound type"""
    wound_type = session.get(WoundTypes, wound_type_id)
    if not wound_type:
        raise HTTPException(status_code=404, detail="Wound type not found")
    return wound_type


@wounds_type_router.get(BASE_URL_WOUNDS_TYPE, response_model=list[WoundTypesPublic])
def get_all_wound_types(
        *,
        session: Session = Depends(Database.get_session),
        offset: int = 0,
        limit: int = Query(default=100, le=100)
):
    """Get all wound types"""
    types = session.exec(select(WoundTypes).offset(offset).limit(limit)).all()
    return types


@wounds_type_router.delete(BASE_URL_WOUNDS_TYPE + "{wound_type_id}")
def delete_wound_type(
        *,
        session: Session = Depends(Database.get_session),
        wound_type_id: int
):
    """Delete wound type"""
    wound_type = session.get(WoundTypes, wound_type_id)
    if not wound_type:
        raise HTTPException(status_code=404, detail="Wound type not found")
    session.delete(wound_type)
    session.commit()
    return {"ok": True}