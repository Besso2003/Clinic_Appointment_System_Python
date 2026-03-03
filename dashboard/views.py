from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def admin_dashboard(request):
	return render(request, 'dashboard/admin.html')

@login_required
def doctor_dashboard(request):
	return render(request, 'dashboard/doctor.html')

@login_required
def receptionist_dashboard(request):
	return render(request, 'dashboard/receptionist.html')

@login_required
def patient_dashboard(request):
	return render(request, 'dashboard/patient.html')
