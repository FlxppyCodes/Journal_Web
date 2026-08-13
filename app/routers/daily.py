from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.auth import verify_token
from app import models, schemas

router = APIRouter(prefix="/daily", tags=["daily"], dependencies=[Depends(verify_token)])


@router.post("/mood")
def log_mood(payload: schemas.MoodIn, db: Session = Depends(get_db)):
    row = db.query(models.MoodLog).filter_by(entry_date=payload.entry_date).first()
    if row:
        row.mood = payload.mood
    else:
        row = models.MoodLog(**payload.model_dump())
        db.add(row)
    db.commit()
    return {"status": "ok", "entry_date": payload.entry_date, "mood": payload.mood}


@router.post("/sleep")
def log_sleep(payload: schemas.SleepIn, db: Session = Depends(get_db)):
    row = db.query(models.SleepLog).filter_by(entry_date=payload.entry_date).first()
    data = payload.model_dump()
    if row:
        for k, v in data.items():
            setattr(row, k, v)
    else:
        row = models.SleepLog(**data)
        db.add(row)
    db.commit()
    return {"status": "ok", "entry_date": payload.entry_date}


@router.post("/habit")
def log_habit(payload: schemas.HabitIn, db: Session = Depends(get_db)):
    row = db.query(models.HabitLog).filter(
        and_(models.HabitLog.entry_date == payload.entry_date,
             models.HabitLog.habit == payload.habit)
    ).first()
    if row:
        row.completed = payload.completed
        row.note = payload.note
    else:
        row = models.HabitLog(**payload.model_dump())
        db.add(row)
    db.commit()
    return {"status": "ok", "habit": payload.habit, "completed": payload.completed}


@router.get("/habit/{entry_date}")
def get_habits_for_day(entry_date: str, db: Session = Depends(get_db)):
    rows = db.query(models.HabitLog).filter_by(entry_date=entry_date).all()
    return [{"habit": r.habit, "completed": r.completed, "note": r.note} for r in rows]


@router.get("/status/{entry_date}")
def day_status(entry_date: str, db: Session = Depends(get_db)):
    """Quick check used by the daily nudge job: what's been logged today?"""
    has_mood = db.query(models.MoodLog).filter_by(entry_date=entry_date).first() is not None
    has_sleep = db.query(models.SleepLog).filter_by(entry_date=entry_date).first() is not None
    habit_count = db.query(models.HabitLog).filter_by(entry_date=entry_date).count()
    return {"entry_date": entry_date, "mood_logged": has_mood, "sleep_logged": has_sleep, "habits_logged": habit_count}


@router.post("/wellness")
def log_wellness(payload: schemas.WellnessIn, db: Session = Depends(get_db)):
    row = db.query(models.WellnessLog).filter(
        and_(models.WellnessLog.entry_date == payload.entry_date,
             models.WellnessLog.category == payload.category)
    ).first()
    if row:
        row.rating = payload.rating
    else:
        row = models.WellnessLog(**payload.model_dump())
        db.add(row)
    db.commit()
    return {"status": "ok", "category": payload.category, "rating": payload.rating}
