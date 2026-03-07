from functools import total_ordering

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime

from unicodedata import category

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/summary", tags=["summary"])

#extract ist eine SQLAlchemy-Funktion die aus einem Datum einzelne Teile rauszieht, z.B. nur den Monat oder das Jahr
#prefix="/smmary" alles Endpoints hier starten mit /summary/


#ge=1, len=12 Monat muss zwischen 1 und 12 liegen, sonst Fehler
#extract("month, ...") filtert nur Ausgaben aus dem gewünschten Monat
#category_map ich baue ein Dictionyry auf {"Food": {"total": 47.80, "count": 3}}
#sorted(..., reverse=True) teuerste kategorie kommt zuerst
#Der List Comprehension [... for cat, data in ....] wandelt das Dictionary in eine Liste von CategorySummary Objekten um
@router.get("/monthly", response_model=schemas.MonthlySummary)
def get_monthly_summary(
        year: int = Query(default=datetime.now().year),
        month: int = Query(default=datetime.now().month, ge=1, le=12),
        db: Session = Depends(get_db),
):
    expenses = (
        db.query(models.Expense)
        .filter(
            extract("year", models.Expense.date) == year,
            extract("month", models.Expense.date) == month,
        )
        .all()
    )

    total_spent = sum(e.amount for e in expenses)

    category_map = {}
    for expense in expenses:
        cat = expense.category
        if cat not in category_map:
            category_map[cat] = {"total": 0.0, "count": 0}
        category_map[cat]["total"] = round(category_map[cat]["total"] + expense.amount, 2)
        category_map[cat]["count"] += 1

    by_category = [
        schemas.CategorySummary(category=cat, total=data["total"], count=data["count"])
        for cat, data in sorted(category_map.items(), key=lambda x: x[1]["total"], reverse=True)
    ]

    return schemas.MonthlySummary(
        year=year,
        month=month,
        total_spent=round(total_spent, 2),
        expense_count=len(expenses),
        by_category=by_category,
    )


#.distinct() gibt jeden Kategorienamen nur einmal zurück, egal wie oft er vorkommt
#[r[0] for r in results] SQLAlchemy gibt Tupel zurück, wir wollen nur den ersten Wert
@router.get("/categories", response_model=list[str])
def get_all_categoris(db: Session = Depends(get_db)):
    results = db.query(models.Expense.category).disctinct().all()
    return sorted([r[0] for r in results])