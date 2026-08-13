import re
from datetime import date
from telegram import Update
from telegram.ext import ContextTypes

from app.bot import api_client, ai

MOOD_MAP = {
    ":d": "great", ":D": "great",
    ":)": "good",
    ":|": "neutral",
    ":(": "bad",
    ":0": "terrible", ":O": "terrible",
}

HABIT_ALIASES = {
    "gym": "gym", "workout": "gym",
    "breathing": "breathing", "breath": "breathing",
    "coding": "coding", "code": "coding",
    "electronics": "electronics", "tinkering": "electronics",
    "socializing": "socializing", "social": "socializing",
    "piano": "piano",
    "guitar": "guitar",
    "content": "content_creation", "content creation": "content_creation",
    "agency": "agency_work", "agency work": "agency_work",
    "manifestation": "manifestation",
    "assignments": "assignments", "assignment": "assignments",
    "yep": "yep_applications", "youth exchange": "yep_applications",
}


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Journal bot's up. Quick-log with plain text:\n"
        "  mood :)\n"
        "  gym done\n"
        "  piano done\n\n"
        "Or use /today for a status check, /ask <question> for anything else."
    )


async def today_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today().isoformat()
    status = await api_client.get(f"/daily/status/{today}")
    habits = await api_client.get(f"/daily/habit/{today}")
    done = [h["habit"] for h in habits if h["completed"]]
    msg = (
        f"Today ({today}):\n"
        f"Mood logged: {'yes' if status['mood_logged'] else 'no'}\n"
        f"Sleep logged: {'yes' if status['sleep_logged'] else 'no'}\n"
        f"Habits done: {', '.join(done) if done else 'none yet'}"
    )
    await update.message.reply_text(msg)


async def ask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text("Usage: /ask <your question>")
        return
    today = date.today()
    week_start = (today - __import__("datetime").timedelta(days=today.weekday())).isoformat()
    week_data = await api_client.get(f"/analytics/week/{week_start}")
    answer = await ai.answer_question(question, week_data)
    await update.message.reply_text(answer)


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    today = date.today().isoformat()

    # mood: "mood :)" or just ":)"
    for symbol, mood in MOOD_MAP.items():
        if symbol.lower() in text and ("mood" in text or text.strip() == symbol.lower()):
            await api_client.post("/daily/mood", {"entry_date": today, "mood": mood})
            await update.message.reply_text(f"Logged mood: {mood}")
            return

    # habit: "<habit> done"
    match = re.match(r"^(.+?)\s+done$", text)
    if match:
        raw_habit = match.group(1).strip()
        habit_key = HABIT_ALIASES.get(raw_habit)
        if habit_key:
            await api_client.post("/daily/habit", {"entry_date": today, "habit": habit_key, "completed": True})
            await update.message.reply_text(f"Logged habit: {habit_key} ✓")
            return

    await update.message.reply_text(
        "Didn't recognize that. Try 'mood :)' or '<habit> done', or use /ask <question>."
    )
