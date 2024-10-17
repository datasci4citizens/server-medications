from datetime import date, datetime
from sqlmodel import SQLModel
from typing import List, Optional

class ActivePrincipleModel(SQLModel):
    code: str
    active_ingredient: str

class PresentationModel(SQLModel):
    value: str

class ComercialNameModel(SQLModel):
    comercial_name: str
    active_principles: List[ActivePrincipleModel]
    presentations: List[PresentationModel]

class DrugRead(SQLModel):
    # start_date: Optional[date]
    # end_date: Optional[date]
    # start_time: Optional[str]
    # frequency: Optional[str]
    # quantity: Optional[str]
    comercial_names: List[ComercialNameModel]


class UserDrugTrackingRead(SQLModel):
    drug_id: int
    created_date: datetime
    took_date: datetime
    is_taken: bool

class CaretakerBase(SQLModel):
    email: str
    name: str
    phone_number: str | None = None

class DiseaseModel(SQLModel):
    disease_id: int
    status: str | None = None
    created_at: datetime
    updated_at: datetime

class UserRead(SQLModel):
    name: str
    email: str
    birth_date: date | None = None
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    caretakers: list[CaretakerBase]
    disease_links: list[DiseaseModel]
    drug_links: list[UserDrugTrackingRead]

class CaretakerCreate(CaretakerBase):
    pass

class CaretakerPublic(CaretakerBase):
    caretaker_id: int
    created_at: datetime
    updated_at: datetime

class CaretakerUpdate(SQLModel):
    email: str | None = None
    name: str | None = None
    phone_number: str | None = None


class UserBase(SQLModel):
    name: str
    email: str
    birth_date: date | None = None
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    accept_tcle: bool

class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    name: str | None = None
    email: str | None = None
    birth_date: datetime | None = None
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    accept_tcle: bool | None = None

class UserPublic(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
