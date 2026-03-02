from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Appointment, Slot

# Read about select_for_update()

@login_required
# require the standard Django permission; groups created by create_groups.py
# assign this codename to receptionists so has_perm() will succeed automatically
@permission_required('appointments.change_appointment', raise_exception=True)
@transaction.atomic
def mark_as_no_show(request, appointment_id):

    if not request.user.groups.filter(name="Receptionist").exists():
        return HttpResponseForbidden("Only receptionist allowed.")

    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    if appointment.status not in ["CONFIRMED"]:
        return HttpResponseForbidden("Invalid transition.")

    appointment.status = "NO_SHOW"
    appointment.save()

    appointment.slot.is_available = True
    appointment.slot.save()

    return HttpResponse("Appointment marked as no show successfully.")

@login_required
@transaction.atomic
def mark_as_completed(request, appointment_id):

    if request.user.role != "D":
        return HttpResponseForbidden("Only doctor allowed.")
    
    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    if appointment.doctor != request.user:
        return HttpResponseForbidden("You can only complete your own appointments.")

    if appointment.status != "CONFIRMED":
        return HttpResponseForbidden("Invalid Transition!")
    
    appointment.status = "COMPLETED"
    appointment.updated_at = timezone.now()
    appointment.save()

    return HttpResponse("Appointment marked as completed successfully.")

@login_required
def show_create_appointment_form(request):
    if request.user.role != "P":
        return HttpResponseForbidden("Only patients can book appointments.")

    # Optional: filter by doctor via GET parameter
    doctor_id = request.GET.get("doctor_id")

    slots = Slot.objects.filter(is_available=True).select_related('doctor_schedule__doctor')
    if doctor_id:
        slots = slots.filter(doctor_schedule__doctor_id=doctor_id)

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



@login_required
@transaction.atomic
def create_appointment(request, slot_id):

    if request.user.role != "P":
        return HttpResponseForbidden("Only patients can book appointments.")

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


    return HttpResponse("list_patient_appointments")


def prevent_double_booking(slot):
    if not slot.is_available:
        raise ValidationError("Slot already booked.")
    
@login_required
@transaction.atomic
def cancel_appointment(request, appointment_id):

    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    if request.user.role == "P" and appointment.patient != request.user:
        return HttpResponseForbidden("You can only cancel your own appointments.")
    elif request.user.role not in ["P", "R"]:
        return HttpResponseForbidden("Only patients or receptionists can cancel appointments.")

    if appointment.status not in ["REQUESTED", "CONFIRMED"]:
        return HttpResponseForbidden("Appointment cannot be cancelled at this stage.")

    appointment.status = "CANCELLED"
    appointment.updated_at = timezone.now()
    appointment.save()

    appointment.slot.is_available = True
    appointment.slot.save()

    return HttpResponse("Appointment cancelled successfully.")


@login_required
@transaction.atomic
def reschedule_appointment(request, appointment_id, new_slot_id):

    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    if request.user != appointment.patient:
        return HttpResponseForbidden("You cannot reschedule this appointment.")

    new_slot = get_object_or_404(
        Slot.objects.select_for_update(),
        id=new_slot_id
    )

    prevent_double_booking(new_slot)

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

@login_required
def confirm_appointment(request, appointment_id):

    if request.user.role != "R":
        return HttpResponseForbidden("Only receptionist can confirm.")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "REQUESTED":
        return HttpResponseForbidden("Only requested appointments can be confirmed.")

    appointment.status = "CONFIRMED"
    appointment.save()

    return redirect("list_today_appointments")

@login_required
def mark_as_checked_in(request, appointment_id):

    if request.user.role != "R":
        return HttpResponseForbidden("Only receptionist allowed.")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "CONFIRMED":
        return HttpResponseForbidden("Appointment must be confirmed first.")

    appointment_datetime = datetime.combine(
        timezone.now().date(),
        appointment.slot.start_time
    )

    appointment_datetime = timezone.make_aware(appointment_datetime)

    allowed_period = appointment_datetime + timedelta(minutes=15)

    if timezone.now() > allowed_period:
        appointment.status = "NO_SHOW"
        appointment.save()
        return HttpResponseForbidden("Patient exceeded 15 min. Marked as NO_SHOW.")

    appointment.status = "CHECKED_IN"
    appointment.save()

    return redirect("list_today_appointments")


@login_required
def list_patient_appointments(request):

    if request.user.role != "P":
        return HttpResponseForbidden("Only patients allowed.")

    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related("doctor", "slot")

    return render(request, "appointments/patient_list.html", {
        "appointments": appointments
    })


@login_required
def list_doctor_appointments(request):

    if request.user.role != "D":
        return HttpResponseForbidden("Only doctors allowed.")

    appointments = Appointment.objects.filter(
        doctor=request.user
    ).select_related("patient", "slot")

    return render(request, "appointments/doctor_list.html", {
        "appointments": appointments
    })

@login_required
def list_today_appointments(request):

    if request.user.role != "R":
        return HttpResponseForbidden("Only receptionist allowed.")

    today = timezone.now().date()

    appointments = Appointment.objects.filter(
        slot__doctor_schedule__day_of_week=today.strftime("%A")
    ).select_related("patient", "doctor", "slot")

    return render(request, "appointments/today_list.html", {
        "appointments": appointments
    })