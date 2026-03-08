from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import date
from datetime import date, timedelta
from .models import Slot
from .models import DoctorSchedule, DoctorScheduleException
from .forms import DoctorScheduleForm
from .services import generate_slots_for_schedule
from appointments.views import handle_errors


@login_required
@handle_errors
def schedule_list(request):

    if request.user.role != 'D':
        raise PermissionError("Doctors only")

    schedules = DoctorSchedule.objects.filter(doctor=request.user)

    exception_schedule_ids = DoctorScheduleException.objects.filter(
        doctor_schedule__doctor=request.user,
        is_working_day=False
    ).values_list("doctor_schedule_id", flat=True)

    return render(request, 'scheduling/schedule_list.html', {
        'schedules': schedules,
        'exception_schedule_ids': exception_schedule_ids
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
        'form': form,
        'schedule': None
    })


@login_required
@handle_errors
def update_doctor_schedule(request, pk):

    if request.user.role != 'D':
        raise PermissionError("Doctors only")

    schedule = DoctorSchedule.objects.get(id=pk, doctor=request.user)

    if request.method == 'POST':
        form = DoctorScheduleForm(request.POST, instance=schedule)

        if form.is_valid():
            form.save()
            return redirect('schedule-list')

    else:
        form = DoctorScheduleForm(instance=schedule)

    return render(request, 'scheduling/schedule_form.html', {
        'form': form,
        'schedule': schedule
    })


@login_required
@handle_errors
def delete_doctor_schedule(request, pk):

    if request.user.role != 'D':
        raise PermissionError("Doctors only")

    schedule = DoctorSchedule.objects.get(id=pk, doctor=request.user)

    if request.method == 'POST':
        schedule.delete()
        return redirect('schedule-list')

    return render(request, 'scheduling/schedule_confirm_delete.html', {
        'schedule': schedule
    })



@login_required
@handle_errors
def make_schedule_exception(request, pk):

    if request.user.role != 'D':
        raise PermissionError("Doctors only")

    schedule = DoctorSchedule.objects.get(id=pk, doctor=request.user)

    today = date.today()
    end_date = today + timedelta(days=14)

    current_date = today

    while current_date <= end_date:

        if current_date.weekday() == schedule.day_of_week:

            DoctorScheduleException.objects.get_or_create(
                doctor_schedule=schedule,
                date=current_date,
                defaults={'is_working_day': False}
            )

            Slot.objects.filter(
                doctor_schedule=schedule,
                date=current_date
            ).delete()

        current_date += timedelta(days=1)

    return redirect('schedule-list')