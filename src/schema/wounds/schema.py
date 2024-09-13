from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

""" SPECIALISTS TABLES """
class SpecialistsBase(SQLModel):
    email: str
    name: str
    phone_number: str
    is_allowed: bool

class SpecialistsCreate(SpecialistsBase):
    pass

class SpecialistsPublic(SpecialistsBase):
    specialist_id: int
    created_at: datetime
    updated_at: datetime

class SpecialistsUpdate(SQLModel):
    email: str | None = None
    name: str | None = None
    phone_number: str | None = None

class Specialists(SpecialistsBase, table=True):
    specialist_id: int = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime

    tracking_records: list["TrackingRecords"] = Relationship(back_populates="specialist")

""" PATIENTS TABLES """
class PatientsBase(SQLModel):
    name: str
    birthday: datetime | None = None
    phone_number: str
    is_smoker: bool
    drink_frequency: str
    observations: str | None = None
    accept_tcle: bool

class PatientsCreate(PatientsBase):
    pass

class PatientsUpdate(SQLModel):
    name: str | None = None
    birthday: datetime | None = None
    phone_number: str | None = None
    is_smoker: bool | None = None
    drink_frequency: str | None = None
    observations: str | None = None
    accept_tcle: bool | None = None

class PatientsPublic(PatientsBase):
    patient_id: int
    created_at: datetime
    updated_at: datetime

class Patients(PatientsBase, table=True):
    patient_id: int = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime

    wounds: list["Wounds"] = Relationship(back_populates="patient")
    tracking_records: list["TrackingRecords"] = Relationship(back_populates="patient")

""" WOUNDTYPEs TABLES """

class WoundTypesBase(SQLModel):
    wound_type_name: str

class WoundTypesCreate(WoundTypesBase):
    pass

class WoundTypesUpdate(SQLModel):
    wound_type_name: str | None = None

class WoundTypesPublic(WoundTypesBase):
    wound_type_id: int

class WoundTypes(WoundTypesBase, table = True):
    wound_type_id: int = Field(default=None, primary_key=True)

    wounds: list["Wounds"] = Relationship(back_populates="wound_type")

""" WOUNDS TABLES """
""" no tutorial do sqlmodel, wounds é o hero e patient e wound_type é o team"""
class WoundsBase(SQLModel):
    wound_location: str
    start_date: datetime
    end_date: datetime | None = None
    patient_id: int = Field(foreign_key="patients.patient_id")
    wound_type_id: int = Field(foreign_key="woundtypes.wound_type_id")

class WoundsCreate(WoundsBase):
    pass

class WoundsUpdate(SQLModel):
    # wound_location: str | None = None # acho que não deveria da pra mudar a localização da ferida
    # start_date: datetime | None = None
    end_date: datetime | None = None
    # wound_type_id: int | None = None

class WoundsPublic(WoundsBase):
    wound_id: int

class Wounds(WoundsBase, table = True):
    wound_id: int = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    patient: Patients = Relationship(back_populates="wounds")
    wound_type: WoundTypes = Relationship(back_populates="wounds")

    tracking_records: list["TrackingRecords"] = Relationship(back_populates="wound")

""" TRACKING RECORDS TABLES"""
class TrackingRecordsBase(SQLModel):
    wound_color: str
    wound_aspect: str
    secretion_amount: str
    smell: str
    temperature: float
    dressing: str | None = None
    wound_length: float
    wound_height: float
    wound_area: float
    image_id: int
    observations: str | None = None
    patient_id: int = Field(foreign_key="patients.patient_id")
    wound_id: int = Field(foreign_key="wounds.wound_id")
    specialist_id: int = Field(foreign_key="specialists.specialist_id")

class TrackingRecordsCreate(TrackingRecordsBase):
    pass

class TrackingRecordsUpdate(SQLModel):
    wound_color: str | None = None
    wound_aspect: str | None = None
    secretion_amount: str | None = None
    smell: str | None = None
    temperature: float | None = None
    dressing: str | None = None
    wound_length: float | None = None
    wound_height: float | None = None
    wound_area: float | None = None
    image_id: int | None = None
    observations: str | None = None

class TrackingRecordsPublic(TrackingRecordsBase):
    tracking_record_id: int
    created_at: datetime

class TrackingRecords(TrackingRecordsBase, table = True):
    tracking_record_id: int = Field(default=None, primary_key=True)
    created_at: datetime
    updated_at: datetime
    patient: Patients = Relationship(back_populates="tracking_records")
    wound: Wounds = Relationship(back_populates="tracking_records")
    specialist: Specialists = Relationship(back_populates="tracking_records")

""" DATA MODELS FOR RELATIONSHIPS """
class PatientsPublicWithWounds(PatientsPublic):
    wounds: list[WoundsPublic] = []

class WoundsPublicWithWoundType(WoundsPublic):
    wound_type: WoundTypes | None = None

class WoundsPublicWithPatient(WoundsPublic):
    patient: PatientsPublic | None = None
    wound_type: WoundTypes | None = None

class WoundsPublicWithTrackingRecords(WoundsPublic):
    tracking_records: list[TrackingRecordsPublic] = []

class SpecialistsPublicWithTrackingRecords(SpecialistsPublic):
    pass
