from datetime import date, datetime
from sqlmodel import Field, SQLModel

class MihUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    name: str = Field(index=True)
    birthday: date | None = Field(default=None)
    phone_number: str | None = Field(default=None)
    created_at: datetime = Field(default=datetime.utcnow)
    updated_at: datetime = Field(default=datetime.utcnow)
    __tablename__ = 'mih_user'