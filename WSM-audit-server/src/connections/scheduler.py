from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

def get_scheduler():
    if scheduler.running:
        return scheduler
    raise Exception("AsyncIO Scheduler is not running. Please, restart the server!")