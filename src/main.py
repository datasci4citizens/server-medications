from fastapi import FastAPI

from db.manager import Database
from api.medication_users import user_router
from api.medication_drugs import drugs_router
from api.medication_caretakers import caretaker_router
from api.medication_schedule import schedule_router
from api.medication_diseases import disease_router

Database.db_engine()

app = FastAPI()

app.include_router(user_router)
app.include_router(drugs_router)
app.include_router(caretaker_router)
app.include_router(schedule_router)
app.include_router(disease_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)