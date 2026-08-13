from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
from app import models, schemas

router = APIRouter(prefix="/planning", tags=["planning"], dependencies=[Depends(verify_token)])


@router.post("/weekly-priority")
def add_priority(payload: schemas.WeeklyPriorityIn, db: Session = Depends(get_db)):
    row = models.WeeklyPriority(**payload.model_dump())
    db.add(row)
    db.commit()
    return {"status": "ok", "id": row.id}


@router.get("/weekly-priority/{week_start}")
def list_priorities(week_start: str, db: Session = Depends(get_db)):
    rows = db.query(models.WeeklyPriority).filter_by(week_start=week_start).all()
    return [{"id": r.id, "text": r.priority_text, "is_done": r.is_done} for r in rows]


@router.patch("/weekly-priority/{priority_id}/toggle")
def toggle_priority(priority_id: int, db: Session = Depends(get_db)):
    row = db.query(models.WeeklyPriority).get(priority_id)
    row.is_done = not row.is_done
    db.commit()
    return {"id": row.id, "is_done": row.is_done}


@router.post("/affirmation")
def set_affirmation(payload: schemas.MonthlyAffirmationIn, db: Session = Depends(get_db)):
    row = db.query(models.MonthlyAffirmation).filter_by(month_start=payload.month_start).first()
    if row:
        row.affirmation_text = payload.affirmation_text
    else:
        row = models.MonthlyAffirmation(**payload.model_dump())
        db.add(row)
    db.commit()
    return {"status": "ok"}


@router.post("/focus")
def add_focus_item(payload: schemas.MonthlyFocusIn, db: Session = Depends(get_db)):
    row = models.MonthlyFocus(**payload.model_dump())
    db.add(row)
    db.commit()
    return {"status": "ok", "id": row.id}


@router.get("/focus/{month_start}")
def list_focus_items(month_start: str, db: Session = Depends(get_db)):
    rows = db.query(models.MonthlyFocus).filter_by(month_start=month_start).all()
    return [{"id": r.id, "text": r.item_text, "type": r.item_type} for r in rows]


@router.post("/reflection")
def set_reflection(payload: schemas.MonthlyReflectionIn, db: Session = Depends(get_db)):
    row = db.query(models.MonthlyReflection).filter_by(month_start=payload.month_start).first()
    data = payload.model_dump()
    if row:
        for k, v in data.items():
            setattr(row, k, v)
    else:
        row = models.MonthlyReflection(**data)
        db.add(row)
    db.commit()
    return {"status": "ok"}


@router.post("/shopping-item")
def add_shopping_item(payload: schemas.ShoppingItemIn, db: Session = Depends(get_db)):
    row = models.ShoppingItem(**payload.model_dump())
    db.add(row)
    db.commit()
    return {"status": "ok", "id": row.id}


@router.get("/shopping-item/{month_start}")
def list_shopping_items(month_start: str, db: Session = Depends(get_db)):
    rows = db.query(models.ShoppingItem).filter_by(month_start=month_start).all()
    return [{"id": r.id, "text": r.item_text, "bought": r.is_bought, "price": r.est_price} for r in rows]


@router.patch("/shopping-item/{item_id}/toggle")
def toggle_shopping_item(item_id: int, db: Session = Depends(get_db)):
    row = db.query(models.ShoppingItem).get(item_id)
    row.is_bought = not row.is_bought
    db.commit()
    return {"id": row.id, "bought": row.is_bought}
