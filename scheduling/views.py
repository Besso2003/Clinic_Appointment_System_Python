from django.shortcuts import render, redirect
from .models import DoctorSchedule
from .forms import DoctorScheduleForm
from .services import generate_slots_for_schedule


def schedule_list(request):
    schedules = DoctorSchedule.objects.all()

    return render(request, 'scheduling/schedule_list.html', {
        'schedules': schedules
    })
    
    
    
def create_doctor_schedule(request):

    if request.method == 'POST':
        form = DoctorScheduleForm(request.POST)

        if form.is_valid():
            schedule = form.save()

            generate_slots_for_schedule(schedule)

            return redirect('schedule-list')

    else:
        form = DoctorScheduleForm()

    return render(request, 'scheduling/schedule_form.html', {
        'form': form
    })
    
    
    
def update_doctor_schedule(request, pk):

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
    
    
    
def delete_doctor_schedule(request, pk):

    schedule = DoctorSchedule.objects.get(id=pk)

    if request.method == 'POST':
        schedule.delete()
        return redirect('schedule-list')

    return render(request, 'scheduling/schedule_confirm_delete.html', {
        'schedule': schedule
    })
    