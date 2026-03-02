from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from .models import ConsultationRecord
from django.urls import reverse_lazy
from django.http import HttpResponse
from appointments.models import Appointment
# Create your views here.

class CreateConsultationRecord(CreateView):
    model = ConsultationRecord
    template_name = 'medical_records/consultationrecord_form.html'
    fields = ['diagnosis', 'notes', 'prescription', 'requested_tests']

    def form_valid(self, form):
        appointment = get_object_or_404(
            Appointment,
            id=self.kwargs['appointment_id']
        )
        form.instance.appointment = appointment
        return super().form_valid(form)
    
    
    def get_success_url(self):
        # Redirect to the detail page of the newly created record
        return reverse_lazy("consultation-view", kwargs={"pk": self.object.pk})


class UpdateConsultationRecord(UpdateView):
    model = ConsultationRecord
    template_name = 'medical_records/consultationrecord_form.html'  
    fields = ['diagnosis', 'notes', 'prescription', 'requested_tests']
    def get_success_url(self):
        # Redirect to the detail page after updating
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