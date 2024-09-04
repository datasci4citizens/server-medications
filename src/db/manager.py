from sqlmodel import create_engine

import db.config as config
from schema.common.users_schema import Users


class Database:
    """Database class to handle database connection and operations"""

    def __init__(self):
        self.engine = create_engine(config.POSTGRES_URL)

    def create_db(self):
        """Create the database and tables that do not exist"""
        Users.metadata.create_all(self.engine)

    # Singleton Database instance attribute
    _db_instance = None

    @staticmethod
    def db_engine():
        """Singleton: get the database instance engine or create a new one"""

        if Database._db_instance is None:
            Database._db_instance = Database()
            Database._db_instance.create_db()

        return Database._db_instance.engine
