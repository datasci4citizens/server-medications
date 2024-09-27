from datetime import  datetime
from sqlmodel import Field, SQLModel, Relationship

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    birth_date: datetime
    created_at: datetime
    updated_at: datetime

class UserCreate(User):
    name: str
    email: str
    birth_date: datetime

class UserPublic(User):
    id: int
    name: str
    email: str
    birth_date: datetime
    created_at: datetime
    updated_at: datetime

class UserUpdate(User):
    name: str
    email: str
    birth_date: datetime