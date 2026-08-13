from sqlalchemy import (
    Column, Integer, String, Date, Time, Boolean, Numeric, Text,
    SmallInteger, TIMESTAMP, UniqueConstraint, CheckConstraint, func
)
from app.database import Base


class MoodLog(Base):
    __tablename__ = "mood_log"
    id = Column(Integer, primary_key=True)
    entry_date = Column(Date, unique=True, nullable=False)
    mood = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    __table_args__ = (
        CheckConstraint("mood IN ('great','good','neutral','bad','terrible')"),
    )


class SleepLog(Base):
    __tablename__ = "sleep_log"
    id = Column(Integer, primary_key=True)
    entry_date = Column(Date, unique=True, nullable=False)
    sleep_start = Column(Time)
    sleep_end = Column(Time)
    duration_hours = Column(Numeric(4, 2))
    quality_note = Column(Text)


class HabitLog(Base):
    __tablename__ = "habit_log"
    id = Column(Integer, primary_key=True)
    entry_date = Column(Date, nullable=False)
    habit = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    note = Column(Text)
    __table_args__ = (UniqueConstraint("entry_date", "habit"),)


class WellnessLog(Base):
    __tablename__ = "wellness_log"
    id = Column(Integer, primary_key=True)
    entry_date = Column(Date, nullable=False)
    category = Column(String, nullable=False)
    rating = Column(SmallInteger, nullable=False)
    __table_args__ = (
        UniqueConstraint("entry_date", "category"),
        CheckConstraint("rating BETWEEN 1 AND 5"),
        CheckConstraint(
            "category IN ('happiness','physical_health','mental_health','productivity','me_time')"
        ),
    )


class WeeklyPriority(Base):
    __tablename__ = "weekly_priorities"
    id = Column(Integer, primary_key=True)
    week_start = Column(Date, nullable=False)
    priority_text = Column(Text, nullable=False)
    is_done = Column(Boolean, default=False)


class MonthlyAffirmation(Base):
    __tablename__ = "monthly_affirmations"
    id = Column(Integer, primary_key=True)
    month_start = Column(Date, unique=True, nullable=False)
    affirmation_text = Column(Text)


class MonthlyFocus(Base):
    __tablename__ = "monthly_focus"
    id = Column(Integer, primary_key=True)
    month_start = Column(Date, nullable=False)
    item_text = Column(Text, nullable=False)
    item_type = Column(String, nullable=False)
    __table_args__ = (CheckConstraint("item_type IN ('focus','distraction')"),)


class MonthlyReflection(Base):
    __tablename__ = "monthly_reflection"
    id = Column(Integer, primary_key=True)
    month_start = Column(Date, unique=True, nullable=False)
    accomplishments = Column(Text)
    gratitude = Column(Text)
    discoveries = Column(Text)
    could_improve = Column(Text)


class ShoppingItem(Base):
    __tablename__ = "shopping_list"
    id = Column(Integer, primary_key=True)
    month_start = Column(Date, nullable=False)
    item_text = Column(Text, nullable=False)
    is_bought = Column(Boolean, default=False)
    est_price = Column(Numeric(10, 2))


class IncomeLog(Base):
    __tablename__ = "income_log"
    id = Column(Integer, primary_key=True)
    month_start = Column(Date, nullable=False)
    source = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    received_on = Column(Date)


class ExpenseLog(Base):
    __tablename__ = "expense_log"
    id = Column(Integer, primary_key=True)
    entry_date = Column(Date, nullable=False)
    category = Column(String)
    amount = Column(Numeric(10, 2), nullable=False)
    note = Column(Text)


class SavingsPlan(Base):
    __tablename__ = "savings_plan"
    id = Column(Integer, primary_key=True)
    month_start = Column(Date, unique=True, nullable=False)
    planned_savings = Column(Numeric(10, 2))
    actual_savings = Column(Numeric(10, 2))
    overspent_amount = Column(Numeric(10, 2))


class AIInsight(Base):
    __tablename__ = "ai_insights"
    id = Column(Integer, primary_key=True)
    generated_at = Column(TIMESTAMP, server_default=func.now())
    scope = Column(String, nullable=False)
    content = Column(Text)
    sent_via_telegram = Column(Boolean, default=False)
    __table_args__ = (CheckConstraint("scope IN ('daily','weekly','monthly')"),)
