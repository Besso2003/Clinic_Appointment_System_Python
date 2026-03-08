from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.urls import reverse_lazy
from django.utils import timezone

from appointments.models import Appointment
from appointments.views import handle_errors
from .models import ConsultationRecord
from .forms import ConsultationRecordForm

class RoleRedirectMixin:
    def handle_no_permission(self):
        user = self.request.user

        if not user.is_authenticated:
            return redirect("login")

        role = getattr(user, "role", None)

        redirects = {
            "A": "admin",
            "R": "receptionist",
            "D": "doctor",
            "P": "patient",
        }

        return redirect(redirects.get(role, "home"))


class CreateConsultationRecord(LoginRequiredMixin, RoleRedirectMixin,PermissionRequiredMixin,  CreateView):
    model = ConsultationRecord
    form_class = ConsultationRecordForm
    template_name = 'medical_records/consultationrecord_form.html'
    permission_required = "medical_records.add_consultationrecord"

    def get_appointment(self):
        return get_object_or_404(
            Appointment,
            id=self.kwargs['appointment_id']
        )

    def has_permission(self):
        if not super().has_permission():
            return False

        appointment = self.get_appointment()
        user = self.request.user
        today = timezone.localdate()

        return (
            user.groups.filter(name="Doctor").exists()
            and appointment.doctor_id == user.id
            and appointment.slot.date == today
        )

    def form_valid(self, form):
        appointment = self.get_appointment()
        form.instance.appointment = appointment
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("consultation-view", kwargs={"pk": self.object.pk})


class UpdateConsultationRecord(LoginRequiredMixin, RoleRedirectMixin,PermissionRequiredMixin, UpdateView):
    model = ConsultationRecord
    form_class = ConsultationRecordForm
    template_name = 'medical_records/consultationrecord_form.html'
    permission_required = "medical_records.change_consultationrecord"

 
    def has_permission(self):
        if not super().has_permission():
            return False

        record = self.get_object()
        appointment = record.appointment
        user = self.request.user
        today = timezone.localdate()

        return (
            user.groups.filter(name="Doctor").exists()
            and appointment.doctor_id == user.id
            and appointment.slot.date == today
        )


    def get_success_url(self):
        return reverse_lazy("consultation-view", kwargs={"pk": self.object.pk})

class ViewConsultationRecord(LoginRequiredMixin, RoleRedirectMixin,PermissionRequiredMixin, DetailView):
    model = ConsultationRecord
    template_name = 'medical_records/consultationrecord_detail.html'
    context_object_name = 'record'
    permission_required = "medical_records.view_consultationrecord"

    def has_permission(self):
        if not super().has_permission():
            return False

        user = self.request.user
        record = self.get_object()
        appointment = record.appointment

        return (
            (user.groups.filter(name="Doctor").exists() and appointment.doctor_id == user.id) or
            (user.groups.filter(name="Patient").exists() and appointment.patient_id == user.id)
        )



class PatientMedicalHistory(LoginRequiredMixin, RoleRedirectMixin,PermissionRequiredMixin, ListView):
    model = ConsultationRecord
    template_name = 'medical_records/patient_medical_history.html'
    context_object_name = 'consultations'
    permission_required = "medical_records.view_consultationrecord"

    def has_permission(self):
        if not super().has_permission():
            return False

        user = self.request.user
        patient_id = int(self.kwargs['patient_id'])

        if user.groups.filter(name="Patient").exists():
            return user.id == patient_id

        if user.groups.filter(name="Doctor").exists():
            return Appointment.objects.filter(
                patient__id=patient_id,
                doctor_id=user.id
            ).exists()

        return False


    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        user = self.request.user
        if user.groups.filter(name="Doctor").exists():
            return ConsultationRecord.objects.filter(
                appointment__patient__id=patient_id,
                appointment__doctor_id=user.id
            )
        else:
            return ConsultationRecord.objects.filter(
                appointment__patient__id=patient_id
            )