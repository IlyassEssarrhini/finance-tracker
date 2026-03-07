from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "sqlite:///finance.db"

eingine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eingine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db # was macht yield ?
    finally:
        db.close()

