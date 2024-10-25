from datetime import date, datetime
from sqlmodel import SQLModel
from typing import List, Optional

# Schema for reading the presentations
class PresentationRead(SQLModel):
    id: int
    value: str

# Schema for reading the commercial names
class ComercialNameReadWithPresentations(SQLModel):
    id: int
    comercial_name: str
    presentations: List[PresentationRead]

class ActivePrincipleRead(SQLModel):
    id: int
    code: str
    active_ingredient: str

class ComercialNameRead(SQLModel):
    id: int
    comercial_name: str
    active_principles: List[ActivePrincipleRead]
    presentations: List[PresentationRead]

# Schema for reading the active principles (all drugs)
class DrugRead(SQLModel):
    id: int
    code: str
    active_ingredient: str

# Schema for reading one drug with all details
class DrugReadWithDetails(DrugRead):
    comercial_names: List[ComercialNameRead]

# Schema for reading the drug use details
class DrugUseRead(SQLModel):
    id: int
    start_date: Optional[date]
    end_date: Optional[date]
    start_time: Optional[str]
    frequency: Optional[str]
    quantity: Optional[str]
    comercial_name: ComercialNameRead
    presentation: PresentationRead 


class CaretakerBase(SQLModel):
    name: str

class DiseaseModel(SQLModel):
    disease_id: int
    status: str | None = None

class UserRead(SQLModel):
    name: str
    email: str | None = None
    birth_date: date | None = None
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    scholarship: str | None = None
    caretakers: list[CaretakerBase]
    disease_links: list[DiseaseModel]

class CaretakerCreate(CaretakerBase):
    pass

class CaretakerPublic(CaretakerBase):
    caretaker_id: int

class CaretakerUpdate(SQLModel):
    name: str | None = None

class UserBase(SQLModel):
    name: str
    email: str
    birth_date: date | None = None
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    scholarship: str | None = None
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
    scholarship: str | None = None
    accept_tcle: bool | None = None

class UserPublic(UserBase):
    id: int
