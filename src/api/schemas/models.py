from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from sqlalchemy import func

""" DRUG TABLES """
class DrugUse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    comercial_name_id: int = Field(foreign_key="comercialnames.id")
    presentation_id: int = Field(foreign_key="presentations.id")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[str] = None
    frequency: Optional[str] = None
    quantity: Optional[str] = None

    # Relationships
    user: "User" = Relationship(back_populates="drug_uses")
    comercial_name: "ComercialNames" = Relationship(back_populates="drug_uses")
    presentation: "Presentations" = Relationship(back_populates="drug_uses")


class Presentations(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    value: str

    # Relationship to DrugUse
    drug_uses: List["DrugUse"] = Relationship(back_populates="presentation")


class ComercialNamesActivePrinciple(SQLModel, table=True):
    active_principle_id: int = Field(foreign_key="activeprinciple.id", primary_key=True)
    comercial_name_id: int = Field(foreign_key="comercialnames.id", primary_key=True)

class ComercialNames(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    comercial_name: str

    active_principles: List["ActivePrinciple"] = Relationship(
        back_populates="comercial_names",
        link_model=ComercialNamesActivePrinciple
        )
    drug_uses: List["DrugUse"] = Relationship(
        back_populates="comercial_name"
        )

class ActivePrinciple(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    active_ingredient: str

    comercial_names: List["ComercialNames"] = Relationship(
        back_populates="active_principles",
        link_model=ComercialNamesActivePrinciple
    )

""" USER TABLES """
class UserCaretaker(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    caretaker_id: int = Field(foreign_key="caretaker.id", primary_key=True)

class Caretaker(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    name: str
    phone_number: Optional[str] = None
    created_at: datetime = Field(default_factory=func.now)
    updated_at: datetime = Field(default_factory=func.now)

    users: List["User"] = Relationship(
        back_populates="caretakers", link_model=UserCaretaker
        )

class UserDisease(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    disease_id: int = Field(foreign_key="disease.id", primary_key=True)
    created_at: datetime = Field(default_factory=func.now)
    updated_at: datetime = Field(default_factory=func.now)
    status: Optional[str] = None

    user: "User" = Relationship(back_populates="disease_links")
    disease: "Disease" = Relationship(back_populates="user_links")

class Disease(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    user_links: List[UserDisease] = Relationship(back_populates="disease")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    birth_date: Optional[date] = None
    phone_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    accept_tcle: bool
    created_at: datetime = Field(default_factory=func.now)
    updated_at: datetime = Field(default_factory=func.now)

    caretakers: List[Caretaker] = Relationship(
        back_populates="users", link_model=UserCaretaker
        )
    disease_links: List[UserDisease] = Relationship(back_populates="user")
    drug_uses: List["DrugUse"] = Relationship(back_populates="user")