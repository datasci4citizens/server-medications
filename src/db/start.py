from sqlmodel import create_engine

import db.config as config
from schema.common.users_schema import Users

engine = create_engine(config.POSTGRES_URL, echo=True)
