from sqlmodel import create_engine, Session

import db.config as config
from api.schemas.models import User, Drug, UserDrug, DrugInteraction, Food, FoodInteraction, Disease, UserDisease, Caretaker, TrackingRecord

class Database:
    """Database class to handle database connection and operations"""

    def __init__(self):
        self.engine = create_engine(config.POSTGRES_URL)

    def create_db(self):
        """Create the database and tables that do not exist"""
        User.metadata.create_all(self.engine)
        Drug.metadata.create_all(self.engine)
        UserDrug.metadata.create_all(self.engine)
        DrugInteraction.metadata.create_all(self.engine)
        Food.metadata.create_all(self.engine)
        FoodInteraction.metadata.create_all(self.engine)
        Disease.metadata.create_all(self.engine)
        UserDisease.metadata.create_all(self.engine)
        Caretaker.metadata.create_all(self.engine)
        TrackingRecord.metadata.create_all(self.engine)
        

    # Singleton Database instance attribute
    _db_instance = None

    @staticmethod
    def db_engine():
        """Singleton: get the database instance engine or create a new one"""

        if Database._db_instance is None:
            Database._db_instance = Database()
            Database._db_instance.create_db()

        return Database._db_instance.engine