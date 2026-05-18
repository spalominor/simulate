import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.models import Base
import pandas as pd

# Docker configuraciones
DATA_DIR = "/data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'simulate.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def iniciar_db():
    Base.metadata.create_all(bind=engine)

def obtener_sesion():
    return SessionLocal()