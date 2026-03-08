from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import DoctorSchedule
from .forms import DoctorScheduleForm
from .services import generate_slots_for_schedule
from appointments.views import handle_errors


@login_required
@handle_errors
def schedule_list(request):
    
    if request.user.role != 'D':
        raise PermissionError("Doctors only")
    
    schedules = DoctorSchedule.objects.filter(doctor=request.user)

    return render(request, 'scheduling/schedule_list.html', {
        'schedules': schedules
    })
    
    
@login_required  
@handle_errors  
def create_doctor_schedule(request):
    
    if request.user.role != 'D':
        raise PermissionError("Doctors only")

    if request.method == 'POST':
        form = DoctorScheduleForm(request.POST)

        if form.is_valid():

            schedule = form.save(commit=False)

            schedule.doctor = request.user   

            schedule.save()

            generate_slots_for_schedule(schedule)

            return redirect('schedule-list')

    else:
        form = DoctorScheduleForm()

    return render(request, 'scheduling/schedule_form.html', {
        'form': form
    })
    
    
@login_required  
@handle_errors  
def update_doctor_schedule(request, pk):
    
    if request.user.role != 'D':
        raise PermissionError("Doctors only")

    schedule = DoctorSchedule.objects.get(id=pk)

    if request.method == 'POST':
        form = DoctorScheduleForm(request.POST, instance=schedule)

        if form.is_valid():
            form.save()
            return redirect('schedule-list')

    else:
        form = DoctorScheduleForm(instance=schedule)

    return render(request, 'scheduling/schedule_form.html', {
        'form': form
    })        
    
    
@login_required    
@handle_errors
def delete_doctor_schedule(request, pk):
    
    if request.user.role != 'D':
        raise PermissionError("Doctors only")

    schedule = DoctorSchedule.objects.get(id=pk)

    if request.method == 'POST':
        schedule.delete()
        return redirect('schedule-list')

    return render(request, 'scheduling/schedule_confirm_delete.html', {
        'schedule': schedule
    })
    