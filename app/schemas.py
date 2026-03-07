from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class ExpenseCreate(BaseModel):
    title: str
    amount: float = Field(..., gt=0)
    category: str
    date: date
    note: Optional[str] = None


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    date: Optional[date] = None
    note: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    date: date
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CategorySummary(BaseModel):
    category: str
    total: float
    count: int


class MonthlySummary(BaseModel):
    year: int
    month: int
    total_spent: float
    expense_count: int
    by_category: list[CategorySummary]