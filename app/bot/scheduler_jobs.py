import os
from datetime import date, timedelta
from telegram import Bot

from app.bot import api_client, ai

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=BOT_TOKEN)


async def send(text: str):
    # Telegram caps messages at 4096 chars; split if a monthly summary runs long
    for i in range(0, len(text), 4000):
        await bot.send_message(chat_id=CHAT_ID, text=text[i:i + 4000])


async def daily_nudge_job():
    today = date.today().isoformat()
    status = await api_client.get(f"/daily/status/{today}")
    missing = []
    if not status["mood_logged"]:
        missing.append("mood")
    if not status["sleep_logged"]:
        missing.append("sleep")
    if status["habits_logged"] == 0:
        missing.append("habits")
    if missing:
        await send(f"Haven't logged {', '.join(missing)} today yet — quick update?")


async def weekly_summary_job():
    today = date.today()
    week_start = (today - timedelta(days=today.weekday())).isoformat()
    data = await api_client.get(f"/analytics/week/{week_start}")
    summary = await ai.generate_weekly_summary(data)
    await api_client.post("/insights/", {"scope": "weekly", "content": summary, "sent_via_telegram": True})
    await send(f"Weekly check-in:\n\n{summary}")


async def monthly_summary_job():
    today = date.today()
    month_start = today.replace(day=1).isoformat()
    data = await api_client.get(f"/analytics/month/{month_start}")
    summary = await ai.generate_monthly_summary(data)
    await api_client.post("/insights/", {"scope": "monthly", "content": summary, "sent_via_telegram": True})
    await send(f"Monthly review:\n\n{summary}")


async def monthly_reflection_nudge_job():
    """Runs on the 28th–30th to prompt filling in the monthly reflection before month-end."""
    await send(
        "A few days left this month — want to fill in your Monthly Reflection "
        "(accomplishments, gratitude, discoveries, what could've gone better)?"
    )
