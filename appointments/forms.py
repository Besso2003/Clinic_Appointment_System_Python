from django import forms
from django.core.exceptions import ValidationError
from .models import Appointment
from scheduling.models import Slot


class AppointmentCreateForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = ["slot"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["slot"].queryset = Slot.objects.filter(is_available=True)

        self.user = user

    def clean_slot(self):
        slot = self.cleaned_data["slot"]

        if not slot.is_available:
            raise ValidationError("This slot is already booked.")

        return slot

    def save(self, commit=True):
        appointment = super().save(commit=False)

        appointment.patient = self.user
        appointment.doctor = self.cleaned_data["slot"].doctor_schedule.doctor
        appointment.status = "REQUESTED"

        if commit:
            appointment.save()
            slot = self.cleaned_data["slot"]
            slot.is_available = False
            slot.save()

        return appointment
    
    
class AppointmentRescheduleForm(forms.Form):

    new_slot = forms.ModelChoiceField(
        queryset=Slot.objects.filter(is_available=True),
        label="Select New Slot"
    )

    def clean_new_slot(self):
        slot = self.cleaned_data["new_slot"]

        if not slot.is_available:
            raise ValidationError("This slot is already booked.")

        return slot