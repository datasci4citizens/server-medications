from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship

########################
""" DRUG TABLES """

class drug(SQLModel, table=True):
    drug_id: int
    code: int
    referece_drug: str
    comercial_name: str
    farmaco: str
    prescription: str
    format: str
    dosage_strengh: str
    route: str
    adult_dosage: str
    pediatric_dosage: str
    contradictions: str
    drug_leaflet_path: str
    is_sus_available: bool
    average_price: float
    expected_effects: str
    adverse_effects: str
    indication_for_use: str
    how_to_take: str
    is_splitable: bool
    is_macerable: bool
    precautions: str

class drug_interaction(SQLModel, table=True):
    drug_a_id: int = Field(foreign_key="drugs.drug_id")
    drug_b_id: int = Field(foreign_key="drugs.drug_id")
    interaction: str

class food_interaction(SQLModel, table=True):
    drug_id: int = Field(foreign_key="drugs.drug_id")
    food_id: int = Field(foreign_key="foods.food_id")
    interaction: str

class food(SQLModel, table=True):
    food_id: int = Field(foreign_key="foods.food_id")
    food_name: str

class disease(SQLModel, table=True):
    disease_id: int 
    disease_name: str 
    description: str | None = None

########################
""" USER TABLES """

class UserBase(SQLModel):
    name: str
    birthday: date | None = None
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    accept_tcle: bool

class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    name: str | None = None
    birthday: datetime | None = None
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    accept_tcle: bool | None = None

class UserPublic(UserBase):
    user_id: int
    created_at: datetime
    updated_at: datetime

class Users(UserBase, table=True):
    patient_id: int
    created_at: datetime
    updated_at: datetime

######################
""" CARETAKER TABLES """

class Caretaker(SQLModel):
    created_at: datetime
    updated_at: datetime

class CaretakerBase(SQLModel):
    email: str
    name: str
    phone_number: str | None = None

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

class Caretaker(CaretakerBase, table=True):
    caretaker_id: int
    created_at: datetime
    updated_at: datetime

######################
""" RELATIONSHIPS TABLES """

class user_disease(SQLModel, table=True):
    user_id: int
    disease_id: int
    created_at: datetime
    updated_at: datetime
    status: str | None

class user_use_drug(SQLModel, table=True):
    user_id: int
    code: int
    created_date: datetime
    start_date: datetime
    end_date: datetime
    frequency: str | None = None

class tracking_records(SQLModel, table=True):
    user_id: int
    code: int
    created_date: datetime
    took_date: datetime
    is_taken: bool

class user_caretaker(SQLModel):
    user_id: int
    caretaker_id: int
