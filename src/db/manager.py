from sqlmodel import create_engine, Session

import db.config as config
from api.schemas.models import *

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
        """Add data to the database"""
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
                    accept_tcle=True,
                    created_at="2021-01-01",
                    updated_at="2021-01-01"
                ),
                User(
                    name="Jane Doe", 
                    email="email2@email.com",  
                    birth_date="1990-01-01",
                    phone_number="123456789",
                    emergency_contact_name="John Doe",
                    emergency_contact_number="987654321",
                    accept_tcle=True,
                    created_at="2021-01-01",
                    updated_at="2021-01-01"
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
                    active_ingredients="levotiroxina", 
                    comercial_names=[
                        ComercialNames(comercial_name="Synthroid",
                                       presentations=[
                                            Presentations(value="25uG"),
                                            Presentations(value="50uG"),
                                            Presentations(value="75uG"),
                                            Presentations(value="100uG")
                                            ]),
                        ComercialNames(comercial_name="Euthyrox",
                                       presentations=[
                                            Presentations(value="25uG"),
                                            Presentations(value="50uG"),
                                            Presentations(value="75uG"),
                                            Presentations(value="100uG")
                                            ]),
                        ComercialNames(comercial_name="Puran T4",
                                       presentations=[
                                            Presentations(value="25uG"),
                                            Presentations(value="50uG"),
                                            Presentations(value="75uG"),
                                            Presentations(value="100uG")
                                            ])]),
                ActivePrinciple(
                    code="73590-58-6", 
                    active_ingredients="omeprazol", 
                    comercial_names=[
                        ComercialNames(comercial_name="Losec", 
                                       presentations=[Presentations(value="20mg")]),
                        ComercialNames(comercial_name="Omeprazol EMS", 
                                       presentations=[Presentations(value="20mg")])
                    ]
                ),
                ActivePrinciple(
                    code="79902-63-9", 
                    active_ingredients="sinvastatina", 
                    comercial_names=[
                        ComercialNames(comercial_name="Zocor",
                            presentations=[
                                Presentations(value="10mg"),
                                Presentations(value="20mg"),
                                Presentations(value="40mg")
                                ]),
                        ComercialNames(comercial_name="Sinvasterol",
                            presentations=[
                                Presentations(value="10mg"),
                                Presentations(value="20mg"),
                                Presentations(value="40mg")
                                ]),
                        ComercialNames(comercial_name="Sinvix",
                            presentations=[
                                Presentations(value="10mg"),
                                Presentations(value="20mg"),
                                Presentations(value="40mg")
                                ])])]
            
            session.add_all(drugs)
            session.commit()
            for drug in drugs:
                session.refresh(drug)

            """ ADD CARETAKERS """
            caretakers = [
                Caretaker(
                    name="Alice Care", 
                    email="alice@caretaker.com", 
                    phone_number="123123123", 
                    created_at="2021-01-01", 
                    updated_at="2021-01-01"
                ),
                Caretaker(
                    name="Bob Care", 
                    email="bob@caretaker.com", 
                    phone_number="456456456", 
                    created_at="2021-01-01", 
                    updated_at="2021-01-01"
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
                    status="Chronic", 
                    created_at="2021-01-01", 
                    updated_at="2021-01-01"
                ),
                UserDisease(
                    user_id=users[1].id, 
                    disease_id=diseases[1].id, 
                    status="Chronic", 
                    created_at="2021-01-01", 
                    updated_at="2021-01-01"
                )
            ]
            session.add_all(user_diseases)
            session.commit()

            # """ TRACK DRUG USAGE """
            # tracking_records = [
            #     UserDrugTracking(
            #         user_id=users[0].id, 
            #         drug_id=drugs[0].id, 
            #         created_date="2021-01-05", 
            #         took_date="2021-01-05", 
            #         is_taken=True
            #     ),
            #     UserDrugTracking(
            #         user_id=users[1].id, 
            #         drug_id=drugs[1].id, 
            #         created_date="2021-01-06", 
            #         took_date="2021-01-06", 
            #         is_taken=False
            #     )
            # ]
            # session.add_all(tracking_records)
            # session.commit()

    # Singleton Database instance attribute
    _db_instance = None

    @staticmethod
    def db_engine():
        """Singleton: get the database instance engine or create a new one"""

        if Database._db_instance is None:
            Database._db_instance = Database()
            Database._db_instance.create_db()
            Database._db_instance.add_data()

        return Database._db_instance.engine