#Ich importiere die Datentypen
#func.now() gibt automatisch die aktuelle Uhrzeit zurück
#Base aus database.py, die Klasse erbt davon, damit SQLAlchemy weiß das das eine DB-Tabelle ost
#Class expense ist meine Tabelle. Jede Instanz davon = eine Zeile in der DB
#__tablename__ legt den Namen der Tabelle an der DB fest
#id ...  created_at sind Splaten in der DB-Tabelle
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True) #wir automatisch hochgezählt
    title = Column(String, nullable=False) #Pflichtfeld (nullable=False)
    amount = Column(Float, nullable=False) #Kommazahl
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String, nullable=True) #optional, darf Leer sein
    created_at = Column(DateTime(timezone=True), server_default=func.now()) #wird automatisch gesetzt wenn ein Eintrag erstellt wird