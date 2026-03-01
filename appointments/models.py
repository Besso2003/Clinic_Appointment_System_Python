
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from scheduling.models import Slot


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("REQUESTED", "Requested"),
        ("CONFIRMED", "Confirmed"),
        ("CHECKED_IN", "Checked In"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
        ("NO_SHOW", "No Show"),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_patient",
        limit_choices_to={"role": "P"}
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_doctor",
        limit_choices_to={"role": "D"}
    )

    slot = models.ForeignKey(
        "scheduling.Slot",
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="REQUESTED"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["slot"],
                name="unique_slot_booking"
            )
        ]

    def clean(self):
        if self.patient.role != "P":
            raise ValidationError("Selected user is not a patient.")

        if self.doctor.role != "D":
            raise ValidationError("Selected user is not a doctor.")

        if self.slot.doctor_schedule.doctor != self.doctor:
            raise ValidationError("Slot does not belong to selected doctor.")

    def __str__(self):
        return f"{self.patient.username} - {self.doctor.username} | {self.status}"
