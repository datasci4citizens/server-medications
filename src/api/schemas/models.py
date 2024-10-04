from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship


""" RELATIONSHIPS TABLES """
class UserDisease(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    disease_id: int = Field(foreign_key="disease.id", primary_key=True)
    created_at: datetime
    updated_at: datetime
    status: str | None

    user: "User" = Relationship(back_populates="disease_links")
    disease: "Disease" = Relationship(back_populates="user_links")

class UserCaretaker(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    caretaker_id: int = Field(foreign_key="caretaker.id", primary_key=True)

    user: "User" =  Relationship(back_populates="caretaker_links")
    caretaker: "Caretaker" = Relationship(back_populates="user_links")

# class TrackingRecords(SQLModel, table=True):
#     user_id: int = Field(foreign_key="user.id", primary_key=True)
#     code: int = Field(foreign_key="drug.id", primary_key=True)
#     created_date: datetime
#     took_date: datetime
#     is_taken: bool

class UserUseDrug(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    drug_id: int = Field(foreign_key="drug.id", primary_key=True)

    drug: "Drug" = Relationship(back_populates="user_links")
    user: "User" = Relationship(back_populates="drug_links")



""" DRUG TABLES """
class DrugActiveIngredient(SQLModel, table=True):
    drug_id: int = Field(foreign_key="drug.id", primary_key=True)
    active_ingredient_id: int = Field(foreign_key="activeingredient.id", primary_key=True)

    drug: "Drug" = Relationship(back_populates="active_ingredient_links")
    active_ingredient: "ActiveIngredient" = Relationship(back_populates="drug_links")

class DrugPresentations(SQLModel, table=True):
    drug_id: int = Field(foreign_key="drug.id", primary_key=True)
    presentation_id: int = Field(foreign_key="presentations.id", primary_key=True)

    drug: "Drug" = Relationship(back_populates="presentations_links")
    presentations: "Presentations" = Relationship(back_populates="drug_links")

class DrugComercialNames(SQLModel, table=True):
    drug_id: int = Field(foreign_key="drug.id", primary_key=True)
    comercial_name_id: int = Field(foreign_key="comercialnames.id", primary_key=True)

    drug: "Drug" = Relationship(back_populates="comercial_names_links")
    comercial_names: "ComercialNames" = Relationship(back_populates="drug_links")	

class ActiveIngredient(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    drug_links: list[DrugActiveIngredient] = Relationship(back_populates="active_ingredient")

class Presentations(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    value: str

    drug_links: list[DrugPresentations] = Relationship(back_populates="presentations")

class ComercialNames(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    comercial_name: str

    drug_links: list[DrugComercialNames] = Relationship(back_populates="comercial_names")

class Drug(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    code: str

    user_links: list[UserUseDrug] = Relationship(back_populates="drug")
    active_ingredient_links: list[DrugActiveIngredient] = Relationship(back_populates="drug")
    presentations_links: list[DrugPresentations] = Relationship(back_populates="drug")
    comercial_names_links: list[DrugComercialNames] = Relationship(back_populates="drug")


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
    id: int
    created_at: datetime
    updated_at: datetime

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    birthday: date | None = None
    phone_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_number: str | None = None
    accept_tcle: bool
    created_at: datetime
    updated_at: datetime

    drug_links: list[UserUseDrug] = Relationship(back_populates="user")
    caretaker_links: list[UserCaretaker] = Relationship(back_populates="user")
    disease_links: list[UserDisease] = Relationship(back_populates="user")

class Disease(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str | None = None

    user_links: list[UserDisease] = Relationship(back_populates="disease")

class UserWithDrugsRead(UserBase):
    drugs: list[Drug]


""" CARETAKER TABLES """
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

class Caretaker(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    name: str
    phone_number: str | None = None
    created_at: datetime
    updated_at: datetime

    user_links: list[UserCaretaker] = Relationship(back_populates="caretaker")