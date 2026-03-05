import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Appointment, Slot

# appointments/views.py
# from django.shortcuts import get_object_or_404, HttpResponse
from django.contrib.auth.decorators import user_passes_test
# from django.db import transaction
from scheduling.models import DoctorSchedule
from scheduling.services import generate_slots_for_schedule  # import your function


def is_admin(user):
    return user.is_superuser  # or you can use another permission check

def handle_errors(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except (PermissionError, ValueError, ValidationError) as e:
            return render(request, "appointments/error.html", {"error_message": str(e)})
        except Exception as e:
            print(f"Unexpected error: {e}")
            return render(request, "appointments/error.html", {"error_message": "Something went wrong. Please try again later."})
    return wrapper

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


    # Optional: filter by doctor via GET parameter
    doctor_id = request.GET.get("doctor_id")

    slots = Slot.objects.filter(is_available=True).select_related('doctor_schedule__doctor')
    if doctor_id:
        slots = slots.filter(doctor_schedule__doctor_id=doctor_id)

    slots = slots.order_by("date", "start_time") 


    # Get all doctors for dropdown
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

    if request.user != appointment.patient:
        raise PermissionError("You are not allowed")

    
    if appointment.status not in ["REQUESTED", "CONFIRMED"]:
        raise ValidationError("SStatus should be requested or confirmed only.")


    new_slot = get_object_or_404(
        Slot.objects.select_for_update(),
        id=new_slot_id
    )

    prevent_double_booking(new_slot)

    if new_slot.doctor_schedule.doctor != appointment.doctor:
        raise ValidationError("Invalid Slot Selection.")


    old_slot = appointment.slot
    old_slot.is_available = True
    old_slot.save()

    appointment.slot = new_slot
    appointment.doctor = new_slot.doctor_schedule.doctor
    appointment.status = "REQUESTED"
    appointment.save()

    new_slot.is_available = False
    new_slot.save()

    return redirect("list_patient_appointments")

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
        "current_status": status_filter  # optional (useful for highlighting active button)
    })

## done
@login_required
@handle_errors
def list_doctor_appointments(request):

    if request.user.role != "D":
        raise PermissionError("Only Doctors Are Allowed")


    status_filter = request.GET.get("status", "REQUESTED")

    appointments = Appointment.objects.filter(
        doctor=request.user,
        status=status_filter
    ).select_related("patient", "slot")

    return render(request, "appointments/doctor_list.html", {
        "appointments": appointments,
        "current_status": status_filter
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
    ).select_related("patient", "doctor", "slot").order_by(
        "slot__date", "slot__start_time"
    )

    status_filter = request.GET.get('status')
    if status_filter == "pending":
        appointments = appointments.filter(status__in=['REQUESTED', 'CONFIRMED'])
    elif status_filter == "checked_in":
        appointments = appointments.filter(status='CHECKED_IN')
    return render(request, "appointments/receptionist_list_appointments.html", {
        "appointments": appointments
    })

## done
@login_required
@handle_errors
def show_reschedule_form(request, appointment_id):

    # if request.user.role != "R":
    #     raise PermissionError("Only Receptionists Are Allowed")

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=request.user
    )

    available_slots = Slot.objects.filter(
        is_available=True,
        doctor_schedule__doctor=appointment.doctor
    ).select_related("doctor_schedule").order_by("date", "start_time")

    return render(request, "appointments/reschedule.html", {
        "appointment": appointment,
        "slots": available_slots
    })

