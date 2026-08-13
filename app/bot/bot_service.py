import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.bot import handlers, scheduler_jobs

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TZ = os.getenv("TIMEZONE", "Asia/Kolkata")


def build_app():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", handlers.start_cmd))
    application.add_handler(CommandHandler("today", handlers.today_cmd))
    application.add_handler(CommandHandler("ask", handlers.ask_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_message))
    return application


async def on_startup(application):
    scheduler = AsyncIOScheduler(timezone=TZ)
    # Daily nudge — 9:30 PM every day
    scheduler.add_job(scheduler_jobs.daily_nudge_job, CronTrigger(hour=21, minute=30))
    # Weekly summary — Sunday 8:00 PM
    scheduler.add_job(scheduler_jobs.weekly_summary_job, CronTrigger(day_of_week="sun", hour=20, minute=0))
    # Monthly summary — 1st of month, 00:05
    scheduler.add_job(scheduler_jobs.monthly_summary_job, CronTrigger(day=1, hour=0, minute=5))
    # Monthly reflection nudge — 28th, 6:00 PM
    scheduler.add_job(scheduler_jobs.monthly_reflection_nudge_job, CronTrigger(day=28, hour=18, minute=0))
    scheduler.start()
    application.bot_data["scheduler"] = scheduler


def main():
    application = build_app()
    application.post_init = on_startup
    application.run_polling()


if __name__ == "__main__":
    main()
