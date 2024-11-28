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
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    observation: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = "Active"

    user: "User" = Relationship(back_populates="drug_uses")
    comercial_name: "ComercialNames" = Relationship(back_populates="drug_uses")
    presentation: "Presentations" = Relationship(back_populates="drug_uses")
    schedules: List["Schedule"] = Relationship(back_populates="drug_use")

class ComercialNamesPresentations(SQLModel, table=True):
    comercial_name_id: int = Field(foreign_key="comercialnames.id", primary_key=True)
    presentation_id: int = Field(foreign_key="presentations.id", primary_key=True)

class Presentations(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    value: str

    comercial_names: List["ComercialNames"] = Relationship(
        back_populates="presentations", 
        link_model=ComercialNamesPresentations
        )
    drug_uses: List["DrugUse"] = Relationship(back_populates="presentation")

class ComercialNamesActivePrinciple(SQLModel, table=True):
    active_principle_id: int = Field(foreign_key="activeprinciple.id", primary_key=True)
    comercial_name_id: int = Field(foreign_key="comercialnames.id", primary_key=True)

class ActivePrinciple(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    active_ingredient: str

    comercial_names: List["ComercialNames"] = Relationship(
        back_populates="active_principles",
        link_model=ComercialNamesActivePrinciple
    )

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
    presentations: List["Presentations"] = Relationship(
        back_populates="comercial_names",
        link_model=ComercialNamesPresentations
        )
    
class Schedule(SQLModel, table=True):   
    """
    This table is used to store the schedule of the user's medication.
    type is either "D" for Day or "H" for Hour.
    value is when the medication should be taken.	
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    drug_use_id: int = Field(foreign_key="druguse.id")
    type: Optional[str] = None
    value: Optional[int] = None

    drug_use: Optional["DrugUse"] = Relationship(back_populates="schedules")

""" USER TABLES """
class UserDisease(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    disease_id: int = Field(foreign_key="disease.id", primary_key=True)
    status: Optional[str] = None

    user: "User" = Relationship(back_populates="disease_links")
    disease: "Disease" = Relationship(back_populates="user_links")

class Disease(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    user_links: List[UserDisease] = Relationship(back_populates="disease")

class UserCaretaker(SQLModel, table=True):
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
    caretaker_id: int = Field(default=None, foreign_key="user.id", primary_key=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[date] = None
    phone_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    accept_tcle: Optional[bool] = None
    scholarship: Optional[str] = None
    gender: Optional[str] = None
    sex: Optional[str] = None
    is_caretaker: Optional[bool] = None

    caretakers: List["User"] = Relationship(
        back_populates="users_cared_for",
        link_model=UserCaretaker,
        sa_relationship_kwargs=dict(
            primaryjoin="User.id==UserCaretaker.caretaker_id",
            secondaryjoin="User.id==UserCaretaker.user_id",
        ),
    )
    users_cared_for: List["User"] = Relationship(
        back_populates="caretakers",
        link_model=UserCaretaker,
        sa_relationship_kwargs=dict(
            primaryjoin="User.id==UserCaretaker.user_id",
            secondaryjoin="User.id==UserCaretaker.caretaker_id",
        ),
    )
    disease_links: List["UserDisease"] = Relationship(back_populates="user")
    drug_uses: List["DrugUse"] = Relationship(back_populates="user")