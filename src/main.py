from fastapi import FastAPI

from db.manager import Database
from api.medication_users import user_router
from api.medication_general import drug_router
Database.db_engine()

app = FastAPI()

app.include_router(user_router)
app.include_router(drug_router)