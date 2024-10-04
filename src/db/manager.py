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
        Drug.metadata.create_all(self.engine)
        Disease.metadata.create_all(self.engine)
        UserDisease.metadata.create_all(self.engine)
        Caretaker.metadata.create_all(self.engine)
        #TrackingRecords.metadata.create_all(self.engine)
    
    def add_data(self):
        """Add data to the database"""
        with Session(self.engine) as session:
            """ ADD USERS """
            user1 = User(name="John Doe", 
                        email="email@email.com", 
                        birth_date="1990-01-01", 
                        phone_number="123456789", 
                        emergency_contact_name="Jane Doe", 
                        emergency_contact_number="987654321", 
                        accept_tcle=True,
                        created_at="2021-01-01",
                        updated_at="2021-01-01")
            session.add(user1)

            user2 = User(name="Jane Doe", 
                        email="email2@email.com",  
                        birth_date="1990-01-01",
                        phone_number="123456789",
                        emergency_contact_name="John Doe",
                        emergency_contact_number="987654321",
                        accept_tcle=True,
                        created_at="2021-01-01",
                        updated_at="2021-01-01")
            session.add(user2)

            session.commit()
            session.refresh(user1)
            session.refresh(user2)
 
            """ ADD DRUGS """
            levotiroxina = Drug(code = "51-48-9")
            levotiroxina_active_ingredient = ActiveIngredient(name="levotiroxina")
            levotiroxina_active_ingredient_link = DrugActiveIngredient(drug=levotiroxina, active_ingredient=levotiroxina_active_ingredient)
            levotiroxina_presentation_25 = Presentations(name="25uG")
            levotiroxina_presentation_50 = Presentations(name="50uG")
            levotiroxina_presentation_75 = Presentations(name="75uG")
            levotiroxina_presentation_100 = Presentations(name="100uG")
            levotiroxina_presentation_link_25 = DrugPresentations(drug=levotiroxina, presentations=levotiroxina_presentation_25)
            levotiroxina_presentation_link_50 = DrugPresentations(drug=levotiroxina, presentations=levotiroxina_presentation_50)
            levotiroxina_presentation_link_75 = DrugPresentations(drug=levotiroxina, presentations=levotiroxina_presentation_75)
            levotiroxina_presentation_link_100 = DrugPresentations(drug=levotiroxina, presentations=levotiroxina_presentation_100)
            levotiroxina_comercial_name_1 = ComercialNames(name="Synthroid")
            levotiroxina_comercial_name_2 = ComercialNames(name="Euthyrox")
            levotiroxina_comercial_name_3 = ComercialNames(name="Puran T4")
            levotiroxina_comercial_name_link_1 = DrugComercialNames(drug=levotiroxina, comercial_names=levotiroxina_comercial_name_1)
            levotiroxina_comercial_name_link_2 = DrugComercialNames(drug=levotiroxina, comercial_names=levotiroxina_comercial_name_2)
            levotiroxina_comercial_name_link_3 = DrugComercialNames(drug=levotiroxina, comercial_names=levotiroxina_comercial_name_3)
            session.add(levotiroxina)
            session.add(levotiroxina_active_ingredient)
            session.add(levotiroxina_active_ingredient_link)
            session.add(levotiroxina_presentation_25)
            session.add(levotiroxina_presentation_50)
            session.add(levotiroxina_presentation_75)
            session.add(levotiroxina_presentation_100)
            session.add(levotiroxina_presentation_link_25)
            session.add(levotiroxina_presentation_link_50)
            session.add(levotiroxina_presentation_link_75)
            session.add(levotiroxina_presentation_link_100)
            session.add(levotiroxina_comercial_name_1)
            session.add(levotiroxina_comercial_name_2)
            session.add(levotiroxina_comercial_name_3)
            session.add(levotiroxina_comercial_name_link_1)
            session.add(levotiroxina_comercial_name_link_2)
            session.add(levotiroxina_comercial_name_link_3)

            omeprazol = Drug(code= "73590-58-6")
            omeprazol_active_ingredient = ActiveIngredient(name="omeprazol")
            omeprazol_active_ingredient_link = DrugActiveIngredient(drug=omeprazol, active_ingredient=omeprazol_active_ingredient)
            omeprazol_presentation_20 = Presentations(name="20mg")
            omeprazol_presentation_link_20 = DrugPresentations(drug=omeprazol, presentations=omeprazol_presentation_20)
            omeprazol_comercial_name_1 = ComercialNames(name="Losec")
            omeprazol_comercial_name_2 = ComercialNames(name="Omeprazol EMS")
            omeprazol_comercial_name_link_1 = DrugComercialNames(drug=omeprazol, comercial_names=omeprazol_comercial_name_1)
            omeprazol_comercial_name_link_2 = DrugComercialNames(drug=omeprazol, comercial_names=omeprazol_comercial_name_2)
            session.add(omeprazol)
            session.add(omeprazol_active_ingredient)
            session.add(omeprazol_active_ingredient_link)
            session.add(omeprazol_presentation_20)
            session.add(omeprazol_presentation_link_20)
            session.add(omeprazol_comercial_name_1)
            session.add(omeprazol_comercial_name_2)
            session.add(omeprazol_comercial_name_link_1)
            session.add(omeprazol_comercial_name_link_2)

            sinvastatina = Drug(code = "79902-63-9")
            sinvastatina_active_ingredient = ActiveIngredient(name="sinvastatina")
            sinvastatina_active_ingredient_link = DrugActiveIngredient(drug=sinvastatina, active_ingredient=sinvastatina_active_ingredient)
            sinvastatina_presentation_10 = Presentations(name="10mg")
            sinvastatina_presentation_20 = Presentations(name="20mg")
            sinvastatina_presentation_40 = Presentations(name="40mg")
            sinvastatina_presentation_link_10 = DrugPresentations(drug=sinvastatina, presentations=sinvastatina_presentation_10)
            sinvastatina_presentation_link_20 = DrugPresentations(drug=sinvastatina, presentations=sinvastatina_presentation_20)
            sinvastatina_presentation_link_40 = DrugPresentations(drug=sinvastatina, presentations=sinvastatina_presentation_40)
            sinvastatina_comercial_name_1 = ComercialNames(name="Zocor")
            sinvastatina_comercial_name_2 = ComercialNames(name="Sinvasterol")
            sinvastatina_comercial_name_3 = ComercialNames(name="Sinvix")
            sinvastatina_comercial_name_link_1 = DrugComercialNames(drug=sinvastatina, comercial_names=sinvastatina_comercial_name_1)
            sinvastatina_comercial_name_link_2 = DrugComercialNames(drug=sinvastatina, comercial_names=sinvastatina_comercial_name_2)
            sinvastatina_comercial_name_link_3 = DrugComercialNames(drug=sinvastatina, comercial_names=sinvastatina_comercial_name_3)
            session.add(sinvastatina)
            session.add(sinvastatina_active_ingredient)
            session.add(sinvastatina_active_ingredient_link)
            session.add(sinvastatina_presentation_10)
            session.add(sinvastatina_presentation_20)
            session.add(sinvastatina_presentation_40)
            session.add(sinvastatina_presentation_link_10)
            session.add(sinvastatina_presentation_link_20)
            session.add(sinvastatina_presentation_link_40)
            session.add(sinvastatina_comercial_name_1)
            session.add(sinvastatina_comercial_name_2)
            session.add(sinvastatina_comercial_name_3)
            session.add(sinvastatina_comercial_name_link_1)
            session.add(sinvastatina_comercial_name_link_2)
            session.add(sinvastatina_comercial_name_link_3)

            session.commit()
            session.refresh(levotiroxina)
            session.refresh(omeprazol)
            session.refresh(sinvastatina)

            """ user1 uses levotiroxina """
            user1_levotiroxina = UserUseDrug(user_id=user1.id, drug_id=levotiroxina.id)
            session.add(user1_levotiroxina)

            """ user1 uses omeprazol """
            user1_omeprazol = UserUseDrug(user_id=user1.id, drug_id=omeprazol.id)
            session.add(user1_omeprazol)

            """ user2 uses sinvastatina """
            user2_sinvastatina = UserUseDrug(user_id=user2.id, drug_id=sinvastatina.id)
            session.add(user2_sinvastatina)

            session.commit()

    # Singleton Database instance attribute
    _db_instance = None

    @staticmethod
    def db_engine():
        """Singleton: get the database instance engine or create a new one"""

        if Database._db_instance is None:
            Database._db_instance = Database()
            # Database._db_instance.create_db()
            # Database._db_instance.add_data()

        return Database._db_instance.engine