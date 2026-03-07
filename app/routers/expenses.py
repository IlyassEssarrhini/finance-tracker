from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/expenses", tags=["Expenses"])

#APIRouter ein Mini-Router nur für Expenses. Später hänge ich ihn in main.py ein
#Depends(get_db)  FastAPI ruft get_db() automatisch auf und gibt uns die DB-Session
#HTTPException damit schicke ich Fehlermeldungen zurück
#prefix="/expenses" alle Endpoints hier starten automatisch mit /expenses/

#POST & GET

@router.get("/", response_model=list[schemas.ExpenseResponse])
def get_expenses(
        category: Optional[str] = Query(None),
        start_date: Optional[datetime] = Query(None), #datetime statt date
        end_date: Optional[datetime] = Query(None), #datetime statt date
        limit: int = Query(50, le=200),
        offset: int = Query(0),
        db: Session = Depends(get_db),
):
    query = db.query(models.Expense)

    if category:
        query = query.filter(models.Expense.category.ilike(f"%{category}%"))
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)

    return query.order_by(models.Expense.date.desc()).offset(offset).limit(limit).all()

#expense.model_dump() wandelt das Pydantic-Objekt in ein Dictionary um und übergibt alle Felder auf einmal an das Model
#db.add() -> db.commit -> db.refresh() das ist immer die Reihenfolge: hinzugügen, speichern, neu laden
#islike Suche ohne Groß-/Kleinschreibung, %food% findet auch "Food" oder "FOOD"
#offset & limit Pagination, damit nicth 10000 Einträge auf einmal geladen werden

@router.get("/{expense_id}", response_model=schemas.ExpenseResponse)
def get_expense(expenses_id: int, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == expenses_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.patch("/{expense_id}", response_model=schemas.ExpenseResponse)
def update_expense(expense_id: int, updates: schemas.ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filer(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense

@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

#/{expenses_id} die ID kommt direkt aus der URL, z.B. /expenses/3
#exclude_unset=True nur die Felder die der User wirklich geschickt hat werden geupdatet, der Rest bleibt unberührt
#setattr(expense, field, value) - setzt dynamisch einen Wert auf das Obejkt
#status_code=204 bedeutet "erfolgreich", aber keine Antwort - Standard beil Delete

@router.post("/", response_model=schemas.ExpenseResponse, status_code=201)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = models.Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense