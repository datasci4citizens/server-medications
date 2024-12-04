from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from db.manager import Database
from db.models import *
from api.schemas import *
from collections import defaultdict
from auth.auth_service import AuthService

schedule_router = APIRouter(dependencies=[Depends(AuthService.get_current_user)])
BASE_URL_SCHEDULE = "/schedule"

#route to return the schedule of a user
@schedule_router.get(f"{BASE_URL_SCHEDULE}/schedule", response_model=list[GroupedScheduleResponse])
def read_user_schedule(request: Request):
    with Session(Database.db_engine()) as session:
        user_id = request.session.get("id")
        # Verify the user exists
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch the user's schedule with all necessary relationships
        schedules = session.exec(
            select(Schedule)
            .join(DrugUse, Schedule.drug_use_id == DrugUse.id)
            .where(DrugUse.user_id == user_id)
            .options(
                selectinload(Schedule.drug_use).selectinload(DrugUse.comercial_name),
                selectinload(Schedule.drug_use).selectinload(DrugUse.presentation)
            )
        ).all()

        # Group schedules by drug_use
        drug_use_schedules = defaultdict(list)
        for schedule in schedules:
            drug_use_schedules[schedule.drug_use_id].append(
                ScheduleItemRead(
                    id=schedule.id,
                    type=schedule.type,
                    value=schedule.value
                )
            )

        # Create the final response structure
        result = []
        for drug_use_id, schedule_items in drug_use_schedules.items():
            # Get the drug_use information from the first schedule in the group
            first_schedule = next(s for s in schedules if s.drug_use_id == drug_use_id)
            
            result.append(
                GroupedScheduleResponse(
                    drug_use=DrugUseRead(
                        id=first_schedule.drug_use.id,
                        start_date=first_schedule.drug_use.start_date,
                        end_date=first_schedule.drug_use.end_date,
                        observation=first_schedule.drug_use.observation,
                        quantity=first_schedule.drug_use.quantity,
                        comercial_name=first_schedule.drug_use.comercial_name,
                        presentation=first_schedule.drug_use.presentation,
                        status="Inactive" if first_schedule.drug_use.end_date else "Active"
                    ),
                    schedules=schedule_items
                )
            )

    return result
    
#drug to create schedule
@schedule_router.post(f"{BASE_URL_SCHEDULE}/schedule", response_model=ScheduleRead)
def create_schedule(request: Request, schedule: ScheduleCreate):
    with Session(Database.db_engine()) as session:
        user_id = request.session.get("id")
        # Verify the user exists
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify the DrugUse exists
        drug_use = session.get(DrugUse, schedule.drug_use_id)
        if not drug_use:
            raise HTTPException(status_code=404, detail="Drug use not found")

        # Create the Schedule object
        created_schedule = Schedule(
            drug_use_id=schedule.drug_use_id,
            type=schedule.type,
            value=schedule.value
        )

        # Add the schedule to the session
        session.add(created_schedule)
        session.commit()
        session.refresh(created_schedule)

        created_schedule = session.exec(
            select(Schedule)
            .where(Schedule.id == created_schedule.id)
            .options(
                selectinload(Schedule.drug_use).selectinload(DrugUse.comercial_name),
                selectinload(Schedule.drug_use).selectinload(DrugUse.presentation)
            )
        ).first()

    return created_schedule

#route to delete a schedule
@schedule_router.delete(f"{BASE_URL_SCHEDULE}/schedule/{{schedule_id}}")
def delete_schedule(request: Request, schedule_id: int):
    with Session(Database.db_engine()) as session:
        user_id = request.session.get("id")
        # Verify the user exists
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify the schedule exists
        schedule = session.get(Schedule, schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        session.delete(schedule)
        session.commit()

        return {"message": "Schedule deleted successfully"}
    
#route to update a schedule
@schedule_router.put(f"{BASE_URL_SCHEDULE}/schedule/{{schedule_id}}", response_model=ScheduleRead)
def update_schedule(request: Request, schedule_id: int, schedule: ScheduleUpdate):
    with Session(Database.db_engine()) as session:
        user_id = request.session.get("id")
        # Verify the user exists
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify the schedule exists
        schedule_db = session.get(Schedule, schedule_id)
        if not schedule_db:
            raise HTTPException(status_code=404, detail="Schedule not found")

        # Update the schedule
        schedule_db.type = schedule.type
        schedule_db.value = schedule.value

        session.add(schedule_db)
        session.commit()
        session.refresh(schedule_db)

        updated_schedule = session.exec(
            select(Schedule)
            .where(Schedule.id == schedule_id)
            .options(
                selectinload(Schedule.drug_use).selectinload(DrugUse.comercial_name),
                selectinload(Schedule.drug_use).selectinload(DrugUse.presentation)
            )
        ).first()

        return updated_schedule