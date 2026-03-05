import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from .models import Appointment, Slot, AppointmentRescheduleHistory
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from scheduling.models import DoctorSchedule
from scheduling.services import generate_slots_for_schedule


def is_admin(user):
    return user.is_superuser

def handle_errors(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)

        except (PermissionError, ValueError, ValidationError) as e:
            home_url = get_home_url(request)
            return render(request, "appointments/error.html", {
                "error_message": str(e),
                "home_url": home_url
            })

        except Exception as e:
            print(f"Unexpected error: {e}")
            home_url = get_home_url(request)
            return render(request, "appointments/error.html", {
                "error_message": "Something went wrong. Please try again later.",
                "home_url": home_url
            })

    return wrapper

def get_home_url(request):
    if request.user.is_authenticated:
        if request.user.role == "R":
            return "receptionist"
        elif request.user.role == "D":
            return "doctor"
        elif request.user.role == "P":
            return "patient"
    return "login"

@login_required
# @user_passes_test(is_admin)
@transaction.atomic
def generate_slots_view(request, schedule_id):
    """
    Generate slots for a given DoctorSchedule for the next 14 days.
    Only accessible to admin users.
    """
    schedule = get_object_or_404(DoctorSchedule, id=schedule_id)
    
    generate_slots_for_schedule(schedule)
    
    return HttpResponse(f"Slots generated successfully for schedule {schedule.id}.")

# Read about select_for_update()

@login_required
# require the standard Django permission; groups created by create_groups.py
# assign this codename to receptionists so has_perm() will succeed automatically
@permission_required('appointments.change_appointment', raise_exception=True)
@transaction.atomic
@handle_errors
def mark_as_no_show(request, appointment_id):

    if not request.user.groups.filter(name="Receptionist").exists():
        raise PermissionError("Only Receptionists can mark no show.")

    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    if appointment.status not in ["CONFIRMED"]:
        raise ValidationError("Appointment must be confirmed first.")

    appointment.status = "NO_SHOW"
    appointment.save()

    appointment.slot.is_available = True
    appointment.slot.save()

    return HttpResponse("Appointment marked as no show successfully.")

## NOT YET
@login_required
@transaction.atomic
@handle_errors
def mark_as_completed(request, appointment_id):

    if request.user.role != "D":
        raise PermissionError("Only doctor allowed.")
    
    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    if appointment.doctor != request.user:
        raise PermissionError("You are not allowed")

    if appointment.status != "CONFIRMED":
        raise ValidationError("Appointment must be confirmed first.")
    
    appointment.status = "COMPLETED"
    appointment.updated_at = timezone.now()
    appointment.save()

    return HttpResponse("Appointment marked as completed successfully.")

## done
@login_required
@handle_errors
def show_create_appointment_form(request):

    if request.user.role != "P":
        raise PermissionError("Only Patients Are Allowed")

    doctor_id = request.GET.get("doctor_id")

    today = timezone.localdate()
    now_time = timezone.localtime().time()

    slots = Slot.objects.filter(
        is_available=True
    ).filter(
        Q(date__gt=today) | Q(date=today, start_time__gt=now_time)
    ).select_related(
        "doctor_schedule__doctor"
    )

    if doctor_id:
        slots = slots.filter(doctor_schedule__doctor_id=doctor_id)

    slots = slots.order_by("date", "start_time")

    from django.contrib.auth import get_user_model
    User = get_user_model()
    doctors = User.objects.filter(role="D")

    context = {
        "slots": slots,
        "doctors": doctors,
        "selected_doctor_id": doctor_id
    }

    return render(request, "appointments/create_appointment.html", context)

## done
@login_required
@transaction.atomic
@handle_errors
def create_appointment(request, slot_id):

    if request.user.role != "P":
        raise PermissionError("Only Patients Are Allowed")


    slot = get_object_or_404(
        Slot.objects.select_for_update(),
        id=slot_id
    )

    prevent_double_booking(slot)

    doctor = slot.doctor_schedule.doctor

    appointment = Appointment.objects.create(
        patient=request.user,
        doctor=doctor,
        slot=slot,
        status="REQUESTED"
    )

    slot.is_available = False
    slot.save()


    return redirect('list_patient_appointments')

def prevent_double_booking(slot):
    if Appointment.objects.filter(slot=slot, status__in=["REQUESTED", "CONFIRMED", "CHECKED_IN"]).exists():
        raise ValidationError("Slot already booked.")


# def prevent_double_booking(slot):

#         if Appointment.objects.filter(slot=slot).exclude(status="CANCELLED").exists():
#          raise ValidationError("Slot already booked.")
    # if not slot.is_available:
    #     raise ValidationError("Slot already booked.")
    
## done
@login_required
@transaction.atomic
@handle_errors
def cancel_appointment(request, appointment_id):

    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    if request.user.role == "P" and appointment.patient != request.user:
        raise PermissionError("You are not allowed")

    elif request.user.role not in ["P", "R", "D"]:
        raise PermissionError("You are not allowed")

    if appointment.status not in ["REQUESTED", "CONFIRMED"]:
        raise ValidationError("Status should be requested or confirmed only.")

    appointment.status = "CANCELLED"
    appointment.updated_at = timezone.now()
    appointment.save()

    appointment.slot.is_available = True
    appointment.slot.save()

    # appointment.delete()

    if request.user.role == "P":
        return redirect('patient')
    elif request.user.role == "R":
        return redirect('list_today_appointments')
    elif request.user.role == "D":
        return redirect('doctor')

## done
@login_required
@transaction.atomic
@handle_errors
def reschedule_appointment(request, appointment_id, new_slot_id):

    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    user = request.user

    is_patient = appointment.patient == user
    is_doctor = appointment.doctor == user
    is_receptionist = user.groups.filter(name="Receptionist").exists()

    if not (is_patient or is_doctor or is_receptionist):
        raise PermissionDenied("You are not allowed to reschedule this appointment.")

    if appointment.status not in ["REQUESTED", "CONFIRMED"]:
        raise ValidationError("Status must be REQUESTED or CONFIRMED only.")

    new_slot = get_object_or_404(
        Slot.objects.select_for_update(),
        id=new_slot_id
    )

    prevent_double_booking(new_slot)

    if new_slot.doctor_schedule.doctor != appointment.doctor:
        raise ValidationError("Invalid slot selection for this doctor.")

    # Free old slot
    old_slot = appointment.slot
    old_slot.is_available = True
    old_slot.save()

    # Update appointment
    appointment.slot = new_slot
    appointment.status = "REQUESTED"
    appointment.save()

    # Mark new slot unavailable
    new_slot.is_available = False
    new_slot.save()

    # Create history
    AppointmentRescheduleHistory.objects.create(
        appointment=appointment,
        old_slot=old_slot,
        new_slot=new_slot,
        changed_by=user,
        reason=request.POST.get("reason", "")
    )

    # Redirect by role
    if is_patient:
        return redirect('patient')
    elif is_doctor:
        return redirect('doctor')
    else:
        return redirect('list_today_appointments')


@login_required
def appointment_details(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related("doctor", "patient", "slot"),
        id=appointment_id
    )

    history = AppointmentRescheduleHistory.objects.filter(
        appointment=appointment
    ).select_related("old_slot", "new_slot", "changed_by").order_by("-id")

    return render(request, "appointments/appointment_details.html", {
        "appointment": appointment,
        "history": history
    })

## done
@login_required
@handle_errors
def confirm_appointment(request, appointment_id):

    if request.user.role not in ["R", "D"]:
        raise PermissionError("You are not allowed")


    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "REQUESTED":
        raise ValidationError("Only requested appointments can be confirmed.")


    appointment.status = "CONFIRMED"
    appointment.save()

    # return redirect("list_today_appointments")
    if request.user.role == "P":
        return redirect('patient')
    elif request.user.role == "R":
        return redirect('list_today_appointments')
    elif request.user.role == "D":
        return redirect('doctor')

## NOT YET
@login_required
@handle_errors
def mark_as_checked_in(request, appointment_id):

    if request.user.role != "R":
        raise PermissionError("Only Receptionists Are Allowed.")


    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "CONFIRMED":
        raise ValidationError("Only Confirmed can be checked in.")


    appointment_datetime = datetime.combine(
        timezone.now().date(),
        appointment.slot.start_time
    )

    appointment_datetime = timezone.make_aware(appointment_datetime)

    allowed_period = appointment_datetime + datetime.timedelta(minutes=15)

    if timezone.now() > allowed_period:
        appointment.status = "NO_SHOW"
        appointment.save()
        return HttpResponseForbidden("Patient exceeded 15 min. Marked as NO_SHOW.")

    appointment.status = "CHECKED_IN"
    appointment.save()

    return redirect("list_today_appointments")

## done
@login_required
@handle_errors
def list_patient_appointments(request):

    if request.user.role != "P":
        raise PermissionError("Only Patients Are Allowed")


    status_filter = request.GET.get("status")

    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related("doctor", "slot").order_by(
        "slot__date", "slot__start_time"
    )

    # Apply filter if status is provided
    if status_filter in ["REQUESTED", "CONFIRMED", "CANCELLED"]:
        appointments = appointments.filter(status=status_filter)

    return render(request, "appointments/patient_list.html", {
        "appointments": appointments,
        "current_status": status_filter
    })

## done
from django.db.models import Q

@login_required
@handle_errors
def list_doctor_appointments(request):

    if request.user.role != "D":
        raise PermissionError("Only Doctors Are Allowed")

    appointments = Appointment.objects.filter(
        doctor=request.user
    ).select_related("patient", "slot")

    status = request.GET.get("status")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    search = request.GET.get("search")

    if status:
        appointments = appointments.filter(status=status)

    if start_date:
        appointments = appointments.filter(slot__date__gte=start_date)

    if end_date:
        appointments = appointments.filter(slot__date__lte=end_date)

    if search:
        appointments = appointments.filter(
            Q(id__icontains=search) |
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search)
        )

    appointments = appointments.order_by("slot__date", "slot__start_time")

    return render(request, "appointments/doctor_list.html", {
        "appointments": appointments
    })

## done
@login_required
@handle_errors
def list_today_appointments(request):

    if request.user.role != "R":
        raise PermissionError("Only Receptionists Are Allowed")

    today = timezone.now().date()
    weekday_number = today.weekday()

    appointments = Appointment.objects.filter(
        slot__doctor_schedule__day_of_week=weekday_number
    ).select_related(
        "patient", "doctor", "slot"
    )

    # GET parameters
    status = request.GET.get("status")
    doctor = request.GET.get("doctor")
    patient = request.GET.get("patient")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    search = request.GET.get("search")

    # Filters
    if status:
        appointments = appointments.filter(status=status)

    if doctor:
        appointments = appointments.filter(doctor_id=doctor)

    if patient:
        appointments = appointments.filter(patient_id=patient)

    if start_date:
        appointments = appointments.filter(slot__date__gte=start_date)

    if end_date:
        appointments = appointments.filter(slot__date__lte=end_date)

    if search:
        appointments = appointments.filter(
            Q(id__icontains=search) |
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search)
        )

    appointments = appointments.order_by("slot__date", "slot__start_time")

    return render(request, "appointments/receptionist_list_appointments.html", {
        "appointments": appointments
    })

## done
@login_required
@handle_errors
def show_reschedule_form(request, appointment_id):


    # if request.user.role != "R":
    #     raise PermissionError("Only Receptionists Are Allowed")


    appointment = get_object_or_404(Appointment, id=appointment_id)

    user = request.user

    is_patient = appointment.patient == user
    is_doctor = appointment.doctor == user
    is_receptionist = user.groups.filter(name="Receptionist").exists()

    if not (is_patient or is_doctor or is_receptionist):
        raise PermissionDenied("You are not allowed to reschedule this appointment.")

    if appointment.status not in ["REQUESTED", "CONFIRMED"]:
        raise ValidationError("Only REQUESTED or CONFIRMED appointments can be rescheduled.")

    today = timezone.localdate()
    now_time = timezone.localtime().time()

    available_slots = Slot.objects.filter(
        is_available=True,
        doctor_schedule__doctor=appointment.doctor
    ).filter(
        Q(date__gt=today) | Q(date=today, start_time__gt=now_time)
    ).exclude(
        id=appointment.slot.id
    ).select_related(
        "doctor_schedule"
    ).order_by("date", "start_time")

    return render(request, "appointments/reschedule.html", {
        "appointment": appointment,
        "slots": available_slots
    })

