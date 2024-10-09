from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import List
from sqlalchemy import func


""" DRUG TABLES """
class DrugPresentations(SQLModel, table=True):
    drug_id: int = Field(foreign_key="drug.id", primary_key=True)
    presentation_id: int = Field(foreign_key="presentations.id", primary_key=True)

class Presentations(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    value: str

    drugs: List["Drug"] = Relationship(back_populates="presentations", link_model=DrugPresentations)

class DrugComercialNames(SQLModel, table=True):
    drug_id: int = Field(foreign_key="drug.id", primary_key=True)
    comercial_name_id: int = Field(foreign_key="comercialnames.id", primary_key=True)	

class ComercialNames(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    comercial_name: str

    drugs: List["Drug"] = Relationship(back_populates="comercial_names", link_model=DrugComercialNames)
    
class DrugActiveIngredient(SQLModel, table=True):
    drug_id: int = Field(foreign_key="drug.id", primary_key=True)
    active_ingredient_id: int = Field(foreign_key="activeingredient.id", primary_key=True)

class ActiveIngredient(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    drugs: List["Drug"] = Relationship(back_populates="active_ingredients", link_model=DrugActiveIngredient)

class Drug(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    code: str

    active_ingredients: List["ActiveIngredient"] = Relationship(back_populates="drugs", link_model=DrugActiveIngredient)
    presentations: List["Presentations"] = Relationship(back_populates="drugs", link_model=DrugPresentations)
    comercial_names: List["ComercialNames"] = Relationship(back_populates="drugs", link_model=DrugComercialNames)
    user_links: List["UserDrugTracking"] = Relationship(back_populates="drug")


""" USER TABLES """
class UserCaretaker(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    caretaker_id: int = Field(foreign_key="caretaker.id", primary_key=True)

class Caretaker(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    name: str
    phone_number: str | None = None
    created_at: datetime = Field(default_factory=func.now)
    updated_at: datetime = Field(default_factory=func.now)

    users: List["User"] = Relationship(back_populates="caretakers", link_model=UserCaretaker)

class UserDisease(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    disease_id: int = Field(foreign_key="disease.id", primary_key=True)
    created_at: datetime = Field(default_factory=func.now)
    updated_at: datetime = Field(default_factory=func.now)
    status: str | None

    user: "User" = Relationship(back_populates="disease_links")
    disease: "Disease" = Relationship(back_populates="user_links")

class Disease(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    user_links: List[UserDisease] = Relationship(back_populates="disease")

class UserDrugTracking(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    drug_id: int = Field(foreign_key="drug.id", primary_key=True)
    created_date: datetime
    took_date: datetime | None = None
    is_taken: bool | None = None  

    drug: "Drug" = Relationship(back_populates="user_links")
    user: "User" = Relationship(back_populates="drug_links")

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    birth_date: date | None = None
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    accept_tcle: bool
    created_at: datetime = Field(default_factory=func.now)
    updated_at: datetime = Field(default_factory=func.now)

    caretakers: List[Caretaker] = Relationship(back_populates="users", link_model=UserCaretaker)
    disease_links: List[UserDisease] = Relationship(back_populates="user")
    drug_links: List["UserDrugTracking"] = Relationship(back_populates="user")