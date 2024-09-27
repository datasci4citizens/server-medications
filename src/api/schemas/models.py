from datetime import  datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    birth_date: datetime
    created_at: datetime
    updated_at: datetime

    # Relationships to other tables
    diseases: List["UserDisease"] = Relationship(back_populates="user")
    drugs: List["UserDrug"] = Relationship(back_populates="user")
    tracking_records: List["TrackingRecord"] = Relationship(back_populates="user")

class UserCreate(SQLModel):
    name: str
    email: str
    birth_date: datetime

class UserPublic(SQLModel):
    name: str
    email: str
    birth_date: datetime

class UserUpdate(SQLModel):
    name: str
    email: str
    birth_date: datetime

class Drug(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: int
    reference_drug: str
    commercial_name: str
    farmaco: str
    prescription: str
    format: str
    dosage_strength: str
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

    # Relationship fields
    food_interactions: List["FoodInteraction"] = Relationship(back_populates="drug")
    drug_interactions: List["DrugInteraction"] = Relationship(back_populates="drug_a")


class DrugInteraction(SQLModel, table=True):
    drug_a_id: int = Field(foreign_key="drug.id", primary_key=True)
    drug_b_id: int = Field(foreign_key="drug.id", primary_key=True)
    interaction: str

    # Relationships
    drug_a: Drug = Relationship(back_populates="drug_interactions")
    drug_b: Drug = Relationship()


class Food(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    food_name: str

    # Backref for interactions
    drugs: List["FoodInteraction"] = Relationship(back_populates="food")


class FoodInteraction(SQLModel, table=True):
    drug_id: int = Field(foreign_key="drug.id", primary_key=True)
    food_id: int = Field(foreign_key="food.id", primary_key=True)
    interaction: str

    # Relationships
    drug: Drug = Relationship(back_populates="food_interactions")
    food: Food = Relationship(back_populates="drugs")


class Disease(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    disease_name: str
    description: Optional[str] = None


class Caretaker(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime


class UserDisease(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    disease_id: int = Field(foreign_key="disease.id", primary_key=True)
    created_at: datetime
    updated_at: datetime
    status: Optional[str] = None

    # Relationship to the User and Disease
    user: User = Relationship(back_populates="diseases")
    disease: "Disease" = Relationship()


class UserDrug(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    drug_id: int = Field(foreign_key="drug.id", primary_key=True)
    created_date: datetime
    start_date: datetime
    end_date: datetime
    frequency: Optional[str] = None

    # Relationship to the User and Drug
    user: User = Relationship(back_populates="drugs")
    drug: "Drug" = Relationship()


class TrackingRecord(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    code: int = Field(primary_key=True)
    created_date: datetime
    took_date: datetime
    is_taken: bool

    # Relationship to the User
    user: User = Relationship(back_populates="tracking_records")