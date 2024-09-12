from datetime import date, datetime
from sqlmodel import Field, SQLModel

class MeidcationUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    name: str = Field(index=True)
    birthday: date | None = Field(default=None)
    phone_number: str | None = Field(default=None)
    emergency_contact_name: str | None = Field(default=None)
    emergency_contact_number: str | None = Field(default=None)
    created_at: datetime = Field(default=datetime.utcnow)
    updated_at: datetime = Field(default=datetime.utcnow)
    accept_tcle: bool = Field(default=False)
    __tablename__ = 'medication_user'