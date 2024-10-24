from fastapi import FastAPI

from db.manager import Database
from api.medication_users import user_router
from api.medication_drugs import drugs_router

Database.db_engine()

app = FastAPI()

app.include_router(user_router)
app.include_router(drugs_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)