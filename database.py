from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
import os

# Lade die Umgebungsvariable für die Datenbank-URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Asynchrone Datenbankverbindung
database = Database(DATABASE_URL)

# SQLAlchemy Engine und Session-Management
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basisklasse für die Models
Base = declarative_base()

# Dependency, um eine DB-Session zu erstellen und später zu schließen
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
