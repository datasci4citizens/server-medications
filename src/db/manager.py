from sqlmodel import create_engine, Session

import db.config as config
from db.models import *

class Database:
    """Database class to handle database connection and operations"""

    def __init__(self):
        self.engine = create_engine(config.POSTGRES_URL)

    def create_db(self):
        """Create the database and tables that do not exist"""
        User.metadata.create_all(self.engine)
        ComercialNames.metadata.create_all(self.engine)
        Caretaker.metadata.create_all(self.engine)
    
    def add_data(self):
        """Add test data to the database"""
        with Session(self.engine) as session:
            """ ADD USERS """
            users = [
                User(
                    name="John Doe", 
                    email="email@email.com", 
                    birth_date="1990-01-01", 
                    phone_number="123456789", 
                    emergency_contact_name="Jane Doe", 
                    emergency_contact_number="987654321", 
                    gender = "M",
                    sex = "M",
                    accept_tcle=True
                ),
                User(
                    name="Jane Doe", 
                    email="email2@email.com",  
                    birth_date="1990-01-01",
                    phone_number="123456789",
                    emergency_contact_name="John Doe",
                    emergency_contact_number="987654321",
                    gender = "F",
                    sex = "F",
                    accept_tcle=True
                )
            ]
            session.add_all(users)
            session.commit()
            session.refresh(users[0])
            session.refresh(users[1])

            """ ADD DRUGS """
            drugs = [
                ActivePrinciple(
                    code="51-48-9", 
                    active_ingredient="levotiroxina", 
                    comercial_names=[
                        ComercialNames(
                            comercial_name="Synthroid", 
                            presentations=[
                                Presentations(value="25uG"),
                                Presentations(value="50uG"),
                                Presentations(value="75uG"),
                                Presentations(value="100uG")
                            ]
                        ),
                        ComercialNames(
                            comercial_name="Euthyrox", 
                            presentations=[
                                Presentations(value="25uG"),
                                Presentations(value="50uG"),
                                Presentations(value="75uG"),
                                Presentations(value="100uG")
                            ]
                        ),
                        ComercialNames(
                            comercial_name="Puran T4", 
                            presentations=[
                                Presentations(value="25uG"),
                                Presentations(value="50uG"),
                                Presentations(value="75uG"),
                                Presentations(value="100uG")
                            ]
                        )
                    ]
                ),
                ActivePrinciple(
                    code="73590-58-6", 
                    active_ingredient="omeprazol", 
                    comercial_names=[
                        ComercialNames(
                            comercial_name="Losec", 
                            presentations=[
                                Presentations(value="20mg")
                            ]
                        ),
                        ComercialNames(
                            comercial_name="Omeprazol EMS", 
                            presentations=[
                                Presentations(value="20mg")
                            ]
                        )
                    ]
                ),
                ActivePrinciple(
                    code="79902-63-9", 
                    active_ingredient="sinvastatina", 
                    comercial_names=[
                        ComercialNames(
                            comercial_name="Zocor", 
                            presentations=[
                                Presentations(value="10mg"),
                                Presentations(value="20mg"),
                                Presentations(value="40mg")
                            ]
                        ),
                        ComercialNames(
                            comercial_name="Sinvasterol", 
                            presentations=[
                                Presentations(value="10mg"),
                                Presentations(value="20mg"),
                                Presentations(value="40mg")
                            ]
                        ),
                        ComercialNames(
                            comercial_name="Sinvix", 
                            presentations=[
                                Presentations(value="10mg"),
                                Presentations(value="20mg"),
                                Presentations(value="40mg")
                            ]
                        )
                    ]
                )
            ]

            session.add_all(drugs)
            session.commit()

            for drug in drugs:
                session.refresh(drug)

            """ ADD CARETAKERS """
            caretakers = [
                Caretaker(
                    name="Alice Care",
                    email = "alice@care.com"
                ),
                Caretaker(
                    name="Bob Care",
                    email = "bob@care.com"
                )
            ]
            session.add_all(caretakers)
            session.commit()
            session.refresh(caretakers[0])
            session.refresh(caretakers[1])

            """ LINK USERS AND CARETAKERS """
            user_caretakers = [
                UserCaretaker(user_id=users[0].id, caretaker_id=caretakers[0].id),
                UserCaretaker(user_id=users[1].id, caretaker_id=caretakers[1].id)
            ]
            session.add_all(user_caretakers)
            session.commit()

            """ ADD DISEASES """
            diseases = [
                Disease(name="Diabetes", 
                        description="A condition that impairs the body's ability to process blood glucose."),
                Disease(name="Hypertension", 
                        description="A condition where the blood pressure in the arteries is elevated.")
            ]
            session.add_all(diseases)
            session.commit()
            session.refresh(diseases[0])
            session.refresh(diseases[1])

            """ LINK USERS AND DISEASES """
            user_diseases = [
                UserDisease(
                    user_id=users[0].id, 
                    disease_id=diseases[0].id, 
                    status="chronic"
                ),
                UserDisease(
                    user_id=users[1].id, 
                    disease_id=diseases[1].id, 
                    status="chronic"
                )
            ]
            session.add_all(user_diseases)
            session.commit()

            # Link Users and Drugs
            drug_use_john = [
                DrugUse(
                    user_id=1, 
                    comercial_name_id=1,  
                    presentation_id=1,   
                    start_date="2024-10-01",
                    quantity="1",
                    status="active"
                ),
                DrugUse(
                    user_id=1,  
                    comercial_name_id=2,  
                    presentation_id=2,   
                    start_date="2024-10-01",
                    quantity="1",
                    status="active"
                )
            ]

            drug_use_jane = [
                DrugUse(
                    user_id=2,  
                    comercial_name_id=3,  
                    presentation_id=3, 
                    start_date="2024-10-01",
                    quantity="1",
                    status="active"
                ),
                DrugUse(
                    user_id=2,  
                    comercial_name_id=4,  
                    presentation_id=4, 
                    start_date="2024-10-01",
                    quantity="1",
                    status="active"
                )
            ]

            session.add_all(drug_use_john)
            session.add_all(drug_use_jane)
            session.commit()

            # Link DrugUse and Schedules
            schedules = [
                Schedule(drug_use_id=drug_use_john[0].id, type="W", value=1),
                Schedule(drug_use_id=drug_use_john[1].id, type="D", value=1),
                Schedule(drug_use_id=drug_use_jane[0].id, type="W", value=4),
                Schedule(drug_use_id=drug_use_jane[1].id, type="D", value=4)
            ]

            session.add_all(schedules)
            session.commit()

    # Singleton Database instance attribute
    _db_instance = None

    @staticmethod
    def db_engine():
        """Singleton: get the database instance engine or create a new one"""

        if Database._db_instance is None:
            Database._db_instance = Database()
            Database._db_instance.create_db()
            #Database._db_instance.add_data()

        return Database._db_instance.engine
    
    @staticmethod
    def get_session():
        with Session(Database.db_engine()) as session:
            yield session