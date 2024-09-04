from datetime import date
from sqlmodel import Field, SQLModel

class Users(SQLModel, table=True):
    email_id: str = Field(default=None, primary_key=True)
    name: str
    birthday: date | None = None
