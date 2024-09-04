from fastapi import FastAPI

import db.start
from api.common.users_api import router

app = FastAPI()

app.include_router(router)
