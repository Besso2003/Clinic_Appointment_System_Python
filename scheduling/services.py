from datetime import date, datetime, timedelta
from django.db import transaction
from django.conf import settings

from .models import Slot, DoctorScheduleException


WINDOW_DAYS = 14  

def generate_slots_for_schedule(schedule):

    today = date.today()
    end_date = today + timedelta(days=WINDOW_DAYS)
    current_date = today
    
    # loop for 14 days
    while current_date <= end_date:

        if current_date.weekday() == schedule.day_of_week:

            exception = DoctorScheduleException.objects.filter(
                doctor_schedule=schedule,
                date=current_date
            ).first()

            if exception and not exception.is_working_day:
                current_date += timedelta(days=1)
                continue

            start_datetime = datetime.combine(current_date, schedule.start_time)
            end_datetime = datetime.combine(current_date, schedule.end_time)

            current_time = start_datetime
            slot_duration = 30
            buffer_minutes = 5
            

            # loop for generating slots for the current day
            while True:
                slot_end = current_time + timedelta(minutes=slot_duration)

                if slot_end > end_datetime:
                    break

                exists = Slot.objects.filter(
                    doctor_schedule=schedule,
                    date=current_date,
                    start_time=current_time.time(),
                    end_time=slot_end.time()
                ).exists()

                if not exists:
                    Slot.objects.create(
                        doctor_schedule=schedule,
                        date=current_date,
                        start_time=current_time.time(),
                        end_time=slot_end.time(),
                        is_available=True
                    )

                current_time = slot_end + timedelta(minutes=buffer_minutes)

        current_date += timedelta(days=1)