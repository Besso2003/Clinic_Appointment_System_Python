from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from appointments.models import Appointment
from appointments.views import get_today_queue, list_patient_appointments
from dashboard.decorators import role_required

# Create your views here.

@login_required
@role_required(["A"])
def admin_dashboard(request):
	return render(request, 'dashboard/admin.html')

from django.utils import timezone

@login_required
@role_required(["D"])
def doctor_dashboard(request):
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
@role_required(["R"])
def receptionist_dashboard(request):
        today_queue = get_today_queue()  # just call the function

        return render(request, "dashboard/receptionist.html", {
            "today_queue": today_queue,
        })
	# return render(request, 'dashboard/receptionist.html')

@login_required
@role_required(["P"])
def patient_dashboard(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related("doctor", "slot")

    return render(request, "dashboard/patient.html", {
        "appointments": appointments
    })