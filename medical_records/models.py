from django.db import models


class ConsultationRecord(models.Model):
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE)
    diagnosis = models.TextField()
    notes = models.TextField()
    prescription = models.TextField()
    requested_tests = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Consultation Record {self.id} for Appointment {self.appointment_id}"