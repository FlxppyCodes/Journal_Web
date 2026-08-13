from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.auth import verify_token
from app import models

router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(verify_token)])

HABITS = [
    "gym", "breathing", "coding", "electronics", "socializing", "piano",
    "guitar", "content_creation", "agency_work", "manifestation",
    "assignments", "yep_applications",
]


@router.get("/week/{week_start}")
def week_analytics(week_start: str, db: Session = Depends(get_db)):
    ws = date.fromisoformat(week_start)
    we = ws + timedelta(days=6)

    moods = db.query(models.MoodLog).filter(
        models.MoodLog.entry_date.between(ws, we)
    ).all()

    habit_rows = db.query(models.HabitLog).filter(
        models.HabitLog.entry_date.between(ws, we)
    ).all()
    habit_totals = {h: {"done": 0, "total": 0} for h in HABITS}
    for row in habit_rows:
        if row.habit in habit_totals:
            habit_totals[row.habit]["total"] += 1
            if row.completed:
                habit_totals[row.habit]["done"] += 1

    wellness_rows = db.query(
        models.WellnessLog.category, func.avg(models.WellnessLog.rating)
    ).filter(
        models.WellnessLog.entry_date.between(ws, we)
    ).group_by(models.WellnessLog.category).all()

    priorities = db.query(models.WeeklyPriority).filter_by(week_start=ws).all()

    sleep_rows = db.query(models.SleepLog).filter(
        models.SleepLog.entry_date.between(ws, we)
    ).all()
    avg_sleep = (
        sum(float(s.duration_hours) for s in sleep_rows if s.duration_hours) / len(sleep_rows)
        if sleep_rows else None
    )

    return {
        "week_start": str(ws),
        "week_end": str(we),
        "moods": [{"date": str(m.entry_date), "mood": m.mood} for m in moods],
        "habit_completion": habit_totals,
        "wellness_averages": {cat: round(float(avg), 2) for cat, avg in wellness_rows},
        "priorities": [
            {"text": p.priority_text, "done": p.is_done} for p in priorities
        ],
        "avg_sleep_hours": round(avg_sleep, 2) if avg_sleep else None,
    }


@router.get("/month/{month_start}")
def month_analytics(month_start: str, db: Session = Depends(get_db)):
    ms = date.fromisoformat(month_start)

    moods = db.query(models.MoodLog).filter(
        func.date_trunc("month", models.MoodLog.entry_date) == ms
    ).all()
    mood_counts: dict[str, int] = {}
    for m in moods:
        mood_counts[m.mood] = mood_counts.get(m.mood, 0) + 1

    habit_rows = db.query(models.HabitLog).filter(
        func.date_trunc("month", models.HabitLog.entry_date) == ms
    ).all()
    habit_totals = {h: {"done": 0, "total": 0} for h in HABITS}
    for row in habit_rows:
        if row.habit in habit_totals:
            habit_totals[row.habit]["total"] += 1
            if row.completed:
                habit_totals[row.habit]["done"] += 1

    wellness_rows = db.query(
        models.WellnessLog.category, func.avg(models.WellnessLog.rating)
    ).filter(
        func.date_trunc("month", models.WellnessLog.entry_date) == ms
    ).group_by(models.WellnessLog.category).all()

    reflection = db.query(models.MonthlyReflection).filter_by(month_start=ms).first()
    affirmation = db.query(models.MonthlyAffirmation).filter_by(month_start=ms).first()
    focus_items = db.query(models.MonthlyFocus).filter_by(month_start=ms).all()

    total_income = db.query(func.coalesce(func.sum(models.IncomeLog.amount), 0)).filter(
        models.IncomeLog.month_start == ms
    ).scalar()
    total_expenses = db.query(func.coalesce(func.sum(models.ExpenseLog.amount), 0)).filter(
        func.date_trunc("month", models.ExpenseLog.entry_date) == ms
    ).scalar()
    savings_plan = db.query(models.SavingsPlan).filter_by(month_start=ms).first()

    return {
        "month_start": str(ms),
        "mood_counts": mood_counts,
        "habit_completion": habit_totals,
        "wellness_averages": {cat: round(float(avg), 2) for cat, avg in wellness_rows},
        "reflection": {
            "accomplishments": reflection.accomplishments if reflection else None,
            "gratitude": reflection.gratitude if reflection else None,
            "discoveries": reflection.discoveries if reflection else None,
            "could_improve": reflection.could_improve if reflection else None,
        } if reflection else None,
        "affirmation": affirmation.affirmation_text if affirmation else None,
        "focus": [f.item_text for f in focus_items if f.item_type == "focus"],
        "distractions": [f.item_text for f in focus_items if f.item_type == "distraction"],
        "finance": {
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "actual_savings": float(total_income - total_expenses),
            "planned_savings": float(savings_plan.planned_savings) if savings_plan and savings_plan.planned_savings else None,
        },
    }
