from fastapi import FastAPI

from db.manager import Database
from api.common.users_api import router

Database.db_engine()

app = FastAPI()

app.include_router(router)
