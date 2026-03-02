
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
        # using group membership keeps logic aligned with create_groups.py
        limit_choices_to={"groups__name": "Patient"}
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_doctor",
        limit_choices_to={"groups__name": "Doctor"}
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
        # ensure group membership rather than relying solely on role field
        if not self.patient.groups.filter(name="Patient").exists():
            raise ValidationError("Selected user is not a patient.")

        if not self.doctor.groups.filter(name="Doctor").exists():
            raise ValidationError("Selected user is not a doctor.")

        if self.slot.doctor_schedule.doctor != self.doctor:
            raise ValidationError("Slot does not belong to selected doctor.")

    def __str__(self):
        return f"{self.patient.username} - {self.doctor.username} | {self.status}"