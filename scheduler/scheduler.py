from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from .jobs import evening_planning_job

# Initialize the scheduler
scheduler = AsyncIOScheduler(timezone="Europe/Bratislava")

def setup_scheduler(bot: Bot):
    """
    Adds jobs to the scheduler and starts it.
    """
    scheduler.add_job(
        evening_planning_job,
        trigger='cron',
        hour=20,  # 8 PM
        minute=0,
        kwargs={'bot': bot, 'scheduler': scheduler} # Pass scheduler to the job
    )

    print("Starting scheduler with evening job...")
    scheduler.start()
    print("Scheduler started.")
