from django import forms
from .models import DoctorSchedule

class DoctorScheduleForm(forms.ModelForm):

    TIME_CHOICES = [
        ("08:00", "08:00 AM"),
        ("09:00", "09:00 AM"),
        ("10:00", "10:00 AM"),
        ("11:00", "11:00 AM"),
        ("12:00", "12:00 PM"),
        ("13:00", "01:00 PM"),
        ("14:00", "02:00 PM"),
        ("15:00", "03:00 PM"),
        ("16:00", "04:00 PM"),
    ]

    start_time = forms.ChoiceField(choices=TIME_CHOICES)
    end_time = forms.ChoiceField(choices=TIME_CHOICES)

    class Meta:
        model = DoctorSchedule
        fields = ['doctor', 'day_of_week', 'start_time', 'end_time']