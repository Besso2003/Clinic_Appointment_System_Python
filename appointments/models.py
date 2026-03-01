#Would uncomment it after finishing doc , patient and slots models

from django.db import models

class Appointment(models.Model):
    STATUS_CHOICES = [
        ("REQUESTED", "Requested"),
        ("CONFIRMED", "Confirmed"),
        ("CHECKED_IN", "Checked In"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
        ("NO_SHOW", "No Show"),
    ]

    # patient = models.ForeignKey(
    #     "User",  
    #     on_delete=models.CASCADE,
    #     related_name="appointments_as_patient"
    # )

    # doctor = models.ForeignKey(
    #     "User",  
    #     on_delete=models.CASCADE,
    #     related_name="appointments_as_doctor"
    # )

    # slot = models.ForeignKey(
    #     "Slot", 
    #     on_delete=models.CASCADE,
    #     related_name="appointments"
    # )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="REQUESTED"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=["slot"],
    #             name="unique_slot_booking"
    #         )
    #     ]

    def __str__(self):
        return f"{self.patient.username} → {self.doctor.username} | {self.status}"