from datetime import date, datetime
from sqlmodel import SQLModel
from typing import List, Optional

# Schema for reading the presentations
class PresentationRead(SQLModel):
    id: int
    concentration: str
    pharmaceutical_form: str

# Schema for reading the commercial names
class ComercialNameReadWithPresentations(SQLModel):
    id: int
    comercial_name: str
    active_principles: List["ActivePrincipleRead"]
    presentations: List[PresentationRead]

class ActivePrincipleRead(SQLModel):
    id: int
    code: str
    active_ingredient: str

class ComercialNameRead(SQLModel):
    id: int
    comercial_name: str
    active_principles: List[ActivePrincipleRead]

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
    start_date: Optional[str]
    end_date: Optional[str]
    observation: Optional[str]
    quantity: Optional[int]
    comercial_name: ComercialNameRead
    presentation: PresentationRead 
    status: Optional[str] 

class CaretakerBase(SQLModel):
    name: str
    email: str

class DiseaseModel(SQLModel):
    disease_id: int
    status: str | None = None

class UserRead(SQLModel):
    id: int
    name: str
    email: str | None = None
    birth_date: date | None = None
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    scholarship: str | None = None
    caretakers: list[CaretakerBase]
    disease_links: list[DiseaseModel]
    gender: str | None
    sex: str | None = None
    is_caretaker: bool | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None

class CaretakerCreate(CaretakerBase):
    pass

class CaretakerPublic(CaretakerBase):
    id: int
    

class CaretakerUpdate(SQLModel):
    name: str | None = None
    email: str | None = None

class UserBase(SQLModel):
    name: str
    email: str 
    birth_date: date | None = None
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    scholarship: str | None = None
    accept_tcle: bool
    gender: str | None
    sex: str | None = None
    is_caretaker: bool | None = None    
    district: str | None = None
    city: str | None = None
    state: str | None = None
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
    gender: str | None
    sex: str | None = None
    is_caretaker: bool | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None
class UserPublic(UserBase):
    id: int

class DrugUseCreate(SQLModel):
    comercial_name_id: int
    presentation_id: int
    start_date: str
    end_date: str
    observation: str
    quantity: int
    status: Optional[str] 

class ComercialNameReadWithoutActivePrinciples(SQLModel):
    id: int
    comercial_name: str

class DrugUseScheduleRead(SQLModel):
    id: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    observation: Optional[str] = None
    quantity: int
    comercial_name: ComercialNameReadWithoutActivePrinciples
    presentation: PresentationRead
    status: Optional[str] 

class ScheduleRead(SQLModel):
    id: int
    drug_use: Optional[DrugUseScheduleRead] = None
    type: Optional[str] = None
    value: Optional[int] = None

class ScheduleCreate(SQLModel):
    drug_use_id: int
    type: Optional[str] = None
    value: Optional[int] = None

class ScheduleUpdate(SQLModel):
    type: str | None = None
    value: int | None = None

class UserDiseaseModel(SQLModel):
    disease_id: int
    status: str | None = None

class DiseaseCreate(SQLModel):
    name: str
    description: Optional[str] = None

class DiseaseUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None

class DiseaseRead(SQLModel):
    id: int
    name: str
    description: Optional[str] = None

class DiseasePublic(DiseaseRead):
    pass

class ScheduleInfo(SQLModel):
    id: int
    type: str
    value: int

class UserScheduleResponse(SQLModel):
    drug_use: DrugUseScheduleRead  # Reference to your existing `DrugUseRead` model
    schedules: List[ScheduleInfo]  # List of schedules associated with this `drug_use`

class ScheduleItemRead(SQLModel):
    id: int
    type: str
    value: float | int | str

class GroupedScheduleResponse(SQLModel):
    drug_use: DrugUseScheduleRead
    schedules: List[ScheduleItemRead]