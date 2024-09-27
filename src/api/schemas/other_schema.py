from datetime import  datetime
from sqlmodel import Field, SQLModel, Relationship

########################
""" DRUG TABLES """

class Drug(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
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

    #food_interactions = list["Food"] = Relationship(back_populates="drug")
    #drug_interactions = list["Drug_interaction"] = Relationship(back_populates="drug")

class Drug_interaction(SQLModel, table=True):
    drug_a_id: int = Field(foreign_key="drug.id")
    drug_b_id: int = Field(foreign_key="drug.id")
    interaction: str

class Food(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    food_name: str

class Food_interaction(SQLModel, table=True):
    drug_id: int = Field(foreign_key="drug.id")
    food_id: int = Field(foreign_key="food.id")
    interaction: str

    drug: Drug = Relationship(back_populates="foods")
    food: Food = Relationship(back_populates="drugs")

class Disease(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    disease_name: str 
    description: str | None = None

######################
""" CARETAKER TABLES """
class Caretaker(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime

######################
""" RELATIONSHIPS TABLES """

class User_Disease(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    disease_id: int = Field(foreign_key="disease.id")
    created_at: datetime
    updated_at: datetime
    status: str | None

class User_Drug(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    drug_id: int = Field(foreign_key="drug.id")
    created_date: datetime
    start_date: datetime
    end_date: datetime
    frequency: str | None = None

class Tracking_records(SQLModel, table=True):
    user_id: int
    code: int
    created_date: datetime
    took_date: datetime
    is_taken: bool