from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from appointments.models import Appointment
from appointments.views import list_patient_appointments

# Create your views here.

@login_required
def admin_dashboard(request):
	return render(request, 'dashboard/admin.html')

from django.utils import timezone

@login_required
def doctor_dashboard(request):

    if request.user.role != "D":
        return HttpResponseForbidden("Only doctors allowed.")

    appointments = Appointment.objects.filter(
        doctor=request.user
    ).select_related("patient", "slot")

    context = {
        "appointments": appointments,
        "todays_appointments": appointments.filter(
            slot__date=timezone.now().date()
        ).count(),
        "total_patients": appointments.values("patient").distinct().count(),
        "pending_appointments": appointments.filter(status="REQUESTED").count(),
    }

    return render(request, "dashboard/doctor.html", context)

@login_required
def receptionist_dashboard(request):
	return render(request, 'dashboard/receptionist.html')

# @login_required
# def patient_dashboard(request):
# 	return render(request, 'dashboard/patient.html')

@login_required
def patient_dashboard(request):

    if request.user.role != "P":
        return HttpResponseForbidden("Only patients allowed.")

    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related("doctor", "slot")

    return render(request, "dashboard/patient.html", {
        "appointments": appointments
    })