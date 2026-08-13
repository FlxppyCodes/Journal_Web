from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.auth import verify_token
from app import models, schemas

router = APIRouter(prefix="/finance", tags=["finance"], dependencies=[Depends(verify_token)])


@router.post("/income")
def add_income(payload: schemas.IncomeIn, db: Session = Depends(get_db)):
    row = models.IncomeLog(**payload.model_dump())
    db.add(row)
    db.commit()
    return {"status": "ok", "id": row.id}


@router.post("/expense")
def add_expense(payload: schemas.ExpenseIn, db: Session = Depends(get_db)):
    row = models.ExpenseLog(**payload.model_dump())
    db.add(row)
    db.commit()
    return {"status": "ok", "id": row.id}


@router.post("/savings-plan")
def set_savings_plan(payload: schemas.SavingsPlanIn, db: Session = Depends(get_db)):
    row = db.query(models.SavingsPlan).filter_by(month_start=payload.month_start).first()
    data = payload.model_dump()
    if row:
        for k, v in data.items():
            setattr(row, k, v)
    else:
        row = models.SavingsPlan(**data)
        db.add(row)
    db.commit()
    return {"status": "ok"}


@router.get("/summary/{month_start}")
def month_summary(month_start: str, db: Session = Depends(get_db)):
    """Raw numbers for the month — AI analysis layer (scheduler script) turns this into narrative."""
    total_income = db.query(func.coalesce(func.sum(models.IncomeLog.amount), 0)).filter(
        models.IncomeLog.month_start == month_start
    ).scalar()

    expenses_by_category = (
        db.query(models.ExpenseLog.category, func.sum(models.ExpenseLog.amount))
        .filter(func.date_trunc("month", models.ExpenseLog.entry_date) == month_start)
        .group_by(models.ExpenseLog.category)
        .all()
    )
    total_expenses = sum(amt for _, amt in expenses_by_category)

    plan = db.query(models.SavingsPlan).filter_by(month_start=month_start).first()

    return {
        "month_start": month_start,
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "expenses_by_category": {cat or "uncategorized": float(amt) for cat, amt in expenses_by_category},
        "planned_savings": float(plan.planned_savings) if plan and plan.planned_savings else None,
        "actual_savings": float(total_income - total_expenses),
        "overspent_amount": float(plan.overspent_amount) if plan and plan.overspent_amount else None,
    }
