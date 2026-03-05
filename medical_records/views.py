from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone

from appointments.models import Appointment
from .models import ConsultationRecord
from .forms import ConsultationRecordForm


class CreateConsultationRecord(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ConsultationRecord
    form_class = ConsultationRecordForm
    template_name = 'medical_records/consultationrecord_form.html'

    def get_appointment(self):
        return get_object_or_404(
            Appointment,
            id=self.kwargs['appointment_id']
        )

    def test_func(self):
        appointment = self.get_appointment()
        user = self.request.user
        today = timezone.localdate()
        #print(appointment.doctor_id, user.id)

        return (
            user.is_authenticated
            and getattr(user, "role", None) == "D"
            and appointment.doctor_id == user.id
            and appointment.slot.date == today
        )

    def handle_no_permission(self):
        user = self.request.user

        if not user.is_authenticated:
            return redirect("login")

        role = getattr(user, "role", None)

        if role == "A":
            return redirect("admin")
        elif role == "D":
            return redirect("doctor")
        elif role == "R":
            return redirect("receptionist")
        elif role == "P":
            return redirect("patient")

        return redirect("home")

    def form_valid(self, form):
        appointment = self.get_appointment()
        form.instance.appointment = appointment
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("consultation-view", kwargs={"pk": self.object.pk})


class UpdateConsultationRecord(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ConsultationRecord
    form_class = ConsultationRecordForm
    template_name = 'medical_records/consultationrecord_form.html'
    def get_appointment(self):
        return get_object_or_404(
            Appointment,
            id=self.kwargs['appointment_id']
        )

    def test_func(self):
        record = self.get_object()
        appointment = record.appointment
        user = self.request.user
        today = timezone.localdate()

        #print(appointment.doctor_id, user.id)

        return (
            user.is_authenticated
            and getattr(user, "role", None) == "D"
            and appointment.doctor_id == user.id
            and appointment.slot.date == today
        )

    def handle_no_permission(self):
        user = self.request.user

        if not user.is_authenticated:
            return redirect("login")

        role = getattr(user, "role", None)

        if role == "A":
            return redirect("admin")
        elif role == "D":
            return redirect("doctor")
        elif role == "R":
            return redirect("receptionist")
        elif role == "P":
            return redirect("patient")

        return redirect("home")

    def get_success_url(self):
        return reverse_lazy("consultation-view", kwargs={"pk": self.object.pk})

class ViewConsultationRecord(DetailView):
    model = ConsultationRecord
    template_name = 'medical_records/consultationrecord_detail.html'
    context_object_name = 'record'


class PatientMedicalHistory(ListView):
    model = ConsultationRecord
    template_name = 'medical_records/patient_medical_history.html'
    context_object_name = 'consultations'

    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return ConsultationRecord.objects.filter(
            appointment__patient__id=patient_id
        ).order_by('-appointment__slot')