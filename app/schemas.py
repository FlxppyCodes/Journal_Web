from datetime import date, time
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MoodIn(BaseModel):
    entry_date: date
    mood: str  # great | good | neutral | bad | terrible


class SleepIn(BaseModel):
    entry_date: date
    sleep_start: Optional[time] = None
    sleep_end: Optional[time] = None
    duration_hours: Optional[float] = None
    quality_note: Optional[str] = None


class HabitIn(BaseModel):
    entry_date: date
    habit: str
    completed: bool = True
    note: Optional[str] = None


class WellnessIn(BaseModel):
    entry_date: date
    category: str  # happiness | physical_health | mental_health | productivity | me_time
    rating: int    # 1-5


class WeeklyPriorityIn(BaseModel):
    week_start: date
    priority_text: str
    is_done: bool = False


class MonthlyAffirmationIn(BaseModel):
    month_start: date
    affirmation_text: str


class MonthlyFocusIn(BaseModel):
    month_start: date
    item_text: str
    item_type: str  # focus | distraction


class MonthlyReflectionIn(BaseModel):
    month_start: date
    accomplishments: Optional[str] = None
    gratitude: Optional[str] = None
    discoveries: Optional[str] = None
    could_improve: Optional[str] = None


class ShoppingItemIn(BaseModel):
    month_start: date
    item_text: str
    is_bought: bool = False
    est_price: Optional[float] = None


class IncomeIn(BaseModel):
    month_start: date
    source: str
    amount: float
    received_on: Optional[date] = None


class ExpenseIn(BaseModel):
    entry_date: date
    category: Optional[str] = None
    amount: float
    note: Optional[str] = None


class SavingsPlanIn(BaseModel):
    month_start: date
    planned_savings: Optional[float] = None
    actual_savings: Optional[float] = None
    overspent_amount: Optional[float] = None


class AIInsightIn(BaseModel):
    scope: str  # daily | weekly | monthly
    content: str
    sent_via_telegram: bool = False


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
