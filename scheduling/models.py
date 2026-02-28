from django.db import models

class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(
        'auth.User',  # until user model created
        on_delete=models.CASCADE
        
        # add role (doctor) when user model created
    )
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()         
    end_time = models.TimeField()           
    is_exception = models.BooleanField(default=False) 

    class Meta:
        unique_together = ('doctor', 'day_of_week', 'start_time', 'end_time')




class Slot(models.Model):
    doctor_schedule = models.ForeignKey(
        'DoctorSchedule', 
        on_delete=models.CASCADE,
        related_name="slots"
    )
    start_time = models.TimeField()      
    end_time = models.TimeField()      
    is_available = models.BooleanField(default=True)  

    class Meta:
        unique_together = ('doctor_schedule', 'start_time', 'end_time')
