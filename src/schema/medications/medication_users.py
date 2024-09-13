from datetime import date, datetime
from sqlmodel import Field, SQLModel

class MedicationUser(SQLModel, table=True):
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

class disease(SQLModel, table=True):
    disease_id: int | None = Field(default=None, primary_key=True)
    disease_name: str = Field(index=True)
    description: str | None = Field(default=None)
    __tablename__ = 'disease'

class user_disease(SQLModel, table=True):
    user_id: int
    disease_id: int
    created_at: datetime = Field(default=datetime.utcnow)
    updated_at: datetime = Field(default=datetime.utcnow)
    status: str | None = Field(default="Active")
    __tablename__ = 'user_disease'

class caretaker(SQLModel, table=True):
    caretaker_id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    name: str = Field(index=True)
    phone_number: str | None = Field(default=None)
    created_at: datetime = Field(default=datetime.utcnow)
    updated_at: datetime = Field(default=datetime.utcnow)
    __tablename__ = 'caretaker'

class user_caretaker(SQLModel, table=True):
    user_id: int
    caretaker_id: int
    __tablename__ = 'user_caretaker'

class user_use_drug(SQLModel, table=True):
    user_id: int
    code: int
    created_date: datetime = Field(default=datetime.utcnow)
    start_date: datetime = Field(default=datetime.utcnow)
    end_date: datetime = Field(default=datetime.utcnow)
    frequency: str | None = Field(default=None)
    __tablename__ = 'user_use_drug'

class tracking_records(SQLModel, table=True):
    user_id: int
    code: int
    created_date: datetime = Field(default=datetime.utcnow)
    took_date: datetime = Field(default=datetime.utcnow)
    is_taken: bool = Field(default=False)
    __tablename__ = 'tracking_records'

class drug(SQLModel, table=True):
    drug_id: int | None = Field(default=None, primary_key=True)
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
    __tablename__ = 'drug'

class drug_interaction(SQLModel, table=True):
    drug_a_id: int
    drug_b_id: int
    interaction: str
    __tablename__ = 'drug_interaction'

class food_interaction(SQLModel, table=True):
    drug_id: int
    food_id: int
    interaction: str
    __tablename__ = 'food_interaction'

class food(SQLModel, table=True):
    food_id: int | None = Field(default=None, primary_key=True)
    food_name: str
    __tablename__ = 'food'