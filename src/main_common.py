from fastapi import FastAPI

from db.manager import Database
from api.common.users_api import router
from api.wounds.wounds_specialist_api import wounds_specialist_router
from api.wounds.wounds_patients_api import wounds_patients_router
from api.wounds.wounds_type_api import wounds_type_router
from api.wounds.wounds_api import wounds_router
from api.wounds.wounds_tracking_records_api import wounds_tracking_records_router

Database.db_engine()

app = FastAPI()

app.include_router(router)
app.include_router(wounds_specialist_router)
app.include_router(wounds_patients_router)
app.include_router(wounds_type_router)
app.include_router(wounds_router)
app.include_router(wounds_tracking_records_router)
