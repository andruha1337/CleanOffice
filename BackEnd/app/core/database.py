from sqlmodel import SQLModel, create_engine, Session
from app.models import models

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

from app.models.models import SystemSetting
from sqlmodel import select

def seed_settings(session: Session):
    defaults = {
        "CO2_WARNING_LIMIT": "1000",
        "CO2_CRITICAL_LIMIT": "1500",
        "SYSTEM_NAME": "CleanOffice Alpha"
    }
    for key, value in defaults.items():
        if not session.get(SystemSetting, key):
            session.add(SystemSetting(key=key, value=value))
    session.commit()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_settings(session)

def get_session():
    with Session(engine) as session:
        yield session
