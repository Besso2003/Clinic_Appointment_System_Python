from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from .models import ConsultationRecord
from django.urls import reverse_lazy
from django.http import HttpResponse
from appointments.models import Appointment
# Create your views here.

from .forms import ConsultationRecordForm

class CreateConsultationRecord(CreateView):
    model = ConsultationRecord
    form_class = ConsultationRecordForm
    template_name = 'medical_records/consultationrecord_form.html'

    def form_valid(self, form):
        appointment = get_object_or_404(
            Appointment,
            id=self.kwargs['appointment_id']
        )
        form.instance.appointment = appointment
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("consultation-view", kwargs={"pk": self.object.pk})


class UpdateConsultationRecord(UpdateView):
    model = ConsultationRecord
    form_class = ConsultationRecordForm
    template_name = 'medical_records/consultationrecord_form.html'

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