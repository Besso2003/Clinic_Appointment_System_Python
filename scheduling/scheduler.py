from apscheduler.schedulers.background import BackgroundScheduler
from .models import DoctorSchedule
from .services import generate_slots_for_schedule


def generate_all_slots():

    schedules = DoctorSchedule.objects.all()

    for schedule in schedules:
        generate_slots_for_schedule(schedule)


def start_scheduler():

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        generate_all_slots,
        'cron',
        hour=0,
        minute=0
    )

    scheduler.start()