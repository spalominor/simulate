from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database.models import Base
import pandas as pd

# 1. Configuración del Engine y la Sesión
DATABASE_URL = "sqlite:///simulate.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Sessionmaker crea una "fábrica" de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def iniciar_db():
    Base.metadata.create_all(bind=engine)

def obtener_sesion():
    return SessionLocal()