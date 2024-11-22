import os 
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from db.manager import Database
from auth.oauth_google import login_router
from api.routers.medication_users import user_router
from api.routers.medication_drugs import drugs_router
from api.routers.medication_caretakers import caretaker_router
from api.routers.medication_schedule import schedule_router
from api.routers.medication_diseases import disease_router

Database.db_engine()

app = FastAPI()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(user_router)
app.include_router(drugs_router)
app.include_router(caretaker_router)
app.include_router(schedule_router)
app.include_router(disease_router)
app.include_router(login_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)