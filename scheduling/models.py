from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class DoctorSchedule(models.Model):

    DAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'D'}
    )

    day_of_week = models.IntegerField(choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('doctor', 'day_of_week', 'start_time', 'end_time')

    def clean(self):
        if self.doctor and self.doctor.role != 'D':
            raise ValidationError("Selected user is not a doctor.")

        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)



class Slot(models.Model):

    doctor_schedule = models.ForeignKey(
        DoctorSchedule,
        on_delete=models.CASCADE
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('doctor_schedule', 'date', 'start_time', 'end_time')

    def clean(self):
        if not self.doctor_schedule:
            return

        if self.start_time >= self.end_time:
            raise ValidationError("Slot start time must be before end time.")

        if (
            self.start_time < self.doctor_schedule.start_time
            or self.end_time > self.doctor_schedule.end_time
        ):
            raise ValidationError("Slot must be within schedule time range.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)




class DoctorScheduleException(models.Model):

    doctor_schedule = models.ForeignKey(
        DoctorSchedule,
        on_delete=models.CASCADE
    )

    date = models.DateField()
    is_working_day = models.BooleanField(default=False)

    class Meta:
        unique_together = ('doctor_schedule', 'date')
