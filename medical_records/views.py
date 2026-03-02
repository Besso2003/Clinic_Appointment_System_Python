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
    success_url = reverse_lazy("consultation-list")

    def form_valid(self, form):
        appointment = get_object_or_404(
            Appointment,
            id=self.kwargs['appointment_id']
        )
        form.instance.appointment = appointment
        return super().form_valid(form)



class UpdateConsultationRecord(UpdateView):
    model = ConsultationRecord
    template_name = 'medical_records/consultationrecord_form.html'  
    fields = ['diagnosis', 'notes', 'prescription', 'requested_tests']
    success_url = reverse_lazy("consultation-list")  

class ViewConsultationRecord(DetailView):
    model = ConsultationRecord
    template_name = 'medical_records/consultationrecord_detail.html'
    context_object_name = 'record'


