import datetime
from urllib import request
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from .models import Appointment, Slot, AppointmentRescheduleHistory
from medical_records.models import ConsultationRecord
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from scheduling.models import DoctorSchedule
from scheduling.services import generate_slots_for_schedule
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from accounts.models import User


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

## done groups and permissions
@login_required
@permission_required("appointments.change_appointment", raise_exception=True)
@transaction.atomic
@handle_errors
def mark_as_no_show(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    now = timezone.now()
    appointment_datetime = datetime.datetime.combine(
        appointment.slot.date,
        appointment.slot.start_time
    )
    appointment_datetime = timezone.make_aware(appointment_datetime)

    allowed_late_period = appointment_datetime + datetime.timedelta(minutes=15)
    if now < allowed_late_period:
        raise ValidationError("Cannot mark as NO_SHOW before patient is 15 minutes late.")

    if request.user.groups.filter(name="Doctor").exists() and appointment.doctor != request.user:
        raise PermissionError("You are not allowed to mark this appointment.")

    if appointment.status != "CONFIRMED":
        raise ValidationError("Only confirmed appointments can be marked as NO_SHOW.")

    appointment.status = "NO_SHOW"
    appointment.updated_at = now
    appointment.save()

    # Free the slot
    appointment.slot.is_available = True
    appointment.slot.save()

    next_url = request.META.get("HTTP_REFERER", reverse("list_today_appointments"))
    return redirect(next_url)

## done groups and permissions
@login_required
@transaction.atomic
@handle_errors
def mark_as_completed(request, appointment_id):

    user = request.user

    if not user.groups.filter(name="Doctor").exists():
        raise PermissionDenied("Only doctors are allowed to mark appointments as completed.")

    # Lock the appointment to prevent race conditions
    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    if appointment.doctor != user:
        raise PermissionDenied("You are not allowed to complete this appointment.")

    if appointment.status != "CHECKED_IN":
        raise ValidationError("Appointment must be checked in first.")

    appointment.status = "COMPLETED"
    appointment.updated_at = timezone.now()
    appointment.save()

    # Redirect to the previous page, or default to doctor appointments list
    next_url = request.META.get('HTTP_REFERER', reverse('list_doctor_appointments'))
    return redirect(next_url)


## done groups and permissions
@login_required
@permission_required("appointments.add_appointment", raise_exception=True)
@handle_errors
def show_create_appointment_form(request):
    """
    Display the appointment creation form for patients.
    Only users with permission to add appointments can access.
    """

    # Ensure the user is a Patient
    if not request.user.groups.filter(name="Patient").exists():
        raise PermissionError("Only Patients are allowed to create appointments.")

    doctor_id = request.GET.get("doctor_id")
    page_number = request.GET.get("page", 1)

    today = timezone.localdate()
    now_time = timezone.localtime().time()

    # Filter available slots
    slots = Slot.objects.filter(is_available=True).filter(
        Q(date__gt=today) | Q(date=today, start_time__gt=now_time)
    ).select_related("doctor_schedule__doctor")

    if doctor_id:
        slots = slots.filter(doctor_schedule__doctor_id=doctor_id)

    slots = slots.order_by("date", "start_time")

    # Pagination: 10 slots per page
    paginator = Paginator(slots, 10)
    page_obj = paginator.get_page(page_number)

    # Get list of doctors
    User = get_user_model()
    doctors = User.objects.filter(groups__name="Doctor")

    context = {
        "slots": page_obj,
        "doctors": doctors,
        "selected_doctor_id": doctor_id,
        "paginator": paginator,
        "page_number": int(page_number),
    }

    return render(request, "appointments/create_appointment.html", context)

## done groups and permissions
@login_required
@transaction.atomic
@permission_required("appointments.add_appointment", raise_exception=True)
@handle_errors
def create_appointment(request, slot_id):
    """
    Creates a new appointment for the logged-in patient.
    Permission-driven: only users with add_appointment permission (Patients) can create.
    """

    # Ensure the user is in the Patient group
    if not request.user.groups.filter(name="Patient").exists():
        raise PermissionDenied("Only Patients are allowed to create appointments.")

    # Lock the slot to prevent race conditions
    slot = get_object_or_404(
        Slot.objects.select_for_update(),
        id=slot_id
    )

    # Prevent double booking
    prevent_double_booking(slot)

    doctor = slot.doctor_schedule.doctor

    # Create the appointment
    appointment = Appointment.objects.create(
        patient=request.user,
        doctor=doctor,
        slot=slot,
        status="REQUESTED"
    )

    # Mark slot as unavailable
    slot.is_available = False
    slot.save()

    return redirect("list_patient_appointments")

def prevent_double_booking(slot):
    if Appointment.objects.filter(slot=slot, status__in=["REQUESTED", "CONFIRMED", "CHECKED_IN"]).exists():
        raise ValidationError("Slot already booked.")

    
## done groups and permissions
@login_required
@transaction.atomic
@permission_required("appointments.change_appointment", raise_exception=True)
@handle_errors
def cancel_appointment(request, appointment_id):

    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    user = request.user
    is_patient = user.groups.filter(name="Patient").exists() and appointment.patient == user
    is_doctor = user.groups.filter(name="Doctor").exists() and appointment.doctor == user
    is_receptionist = user.groups.filter(name="Receptionist").exists()

    if not (is_patient or is_doctor or is_receptionist):
        raise PermissionDenied("You are not allowed to cancel this appointment.")

    if appointment.status not in ["REQUESTED", "CONFIRMED"]:
        raise ValidationError("Appointment status must be REQUESTED or CONFIRMED to cancel.")

    # Update appointment
    appointment.status = "CANCELLED"
    appointment.updated_at = timezone.now()
    appointment.save()

    # Free the slot
    appointment.slot.is_available = True
    appointment.slot.save()

    if is_patient:
        return redirect("list_patient_appointments")
    elif is_doctor:
        return redirect("list_doctor_appointments")
    else:
        return redirect("list_today_appointments")

## done groups and permissions
@login_required
@transaction.atomic
@permission_required("appointments.change_appointment", raise_exception=True)
@handle_errors
def reschedule_appointment(request, appointment_id, new_slot_id):

    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )
    user = request.user

    is_patient = appointment.patient == user and user.groups.filter(name="Patient").exists()
    is_doctor = appointment.doctor == user and user.groups.filter(name="Doctor").exists()
    is_receptionist = user.groups.filter(name="Receptionist").exists()

    if not (is_patient or is_doctor or is_receptionist):
        raise PermissionDenied("You are not allowed to reschedule this appointment.")

    if appointment.status != "REQUESTED":
        raise ValidationError("Status must be REQUESTED only.")

    new_slot = get_object_or_404(
        Slot.objects.select_for_update(),
        id=new_slot_id
    )

    prevent_double_booking(new_slot)

    # Ensure new slot belongs to the same doctor
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

    AppointmentRescheduleHistory.objects.create(
        appointment=appointment,
        old_slot=old_slot,
        new_slot=new_slot,
        changed_by=user,
        reason=request.POST.get("reason", "")
    )

    if is_patient:
        return redirect('list_patient_appointments')
    elif is_doctor:
        return redirect('list_doctor_appointments')
    else:
        return redirect('list_today_appointments')

## done groups and permissions
@login_required
@handle_errors
def appointment_details(request, appointment_id):

    appointment = get_object_or_404(
        Appointment.objects.select_related("doctor", "patient", "slot"),
        id=appointment_id
    )

    user = request.user
    is_patient = user.groups.filter(name="Patient").exists() and appointment.patient == user
    is_doctor = user.groups.filter(name="Doctor").exists() and appointment.doctor == user
    is_receptionist = user.groups.filter(name="Receptionist").exists()

    if not (is_patient or is_doctor or is_receptionist):
        raise PermissionDenied("You are not allowed to view this appointment.")

    history = AppointmentRescheduleHistory.objects.filter(
        appointment=appointment
    ).select_related("old_slot", "new_slot", "changed_by").order_by("-id")

    try:
        consultation_record = appointment.consultationrecord
    except ConsultationRecord.DoesNotExist:
        consultation_record = None

    return render(request, "appointments/appointment_details.html", {
        "appointment": appointment,
        "history": history,
        "consultation_record": consultation_record,
    })

## done groups and permissions
@login_required
@handle_errors
def confirm_appointment(request, appointment_id):

    user = request.user

    if not (user.groups.filter(name="Receptionist").exists() or
            user.groups.filter(name="Doctor").exists()):
        raise PermissionDenied("You are not allowed to confirm appointments.")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "REQUESTED":
        raise ValidationError("Only requested appointments can be confirmed.")

    appointment.status = "CONFIRMED"
    appointment.save()

    if user.groups.filter(name="Receptionist").exists():
        return redirect('list_today_appointments')
    else:
        return redirect('list_doctor_appointments')

## done groups and permissions
@login_required
@handle_errors
@transaction.atomic
def mark_as_checked_in(request, appointment_id):

    user = request.user

    if not user.groups.filter(name="Receptionist").exists():
        raise PermissionDenied("Only Receptionists are allowed to check in appointments.")

    # Lock the appointment to avoid race conditions
    appointment = get_object_or_404(
        Appointment.objects.select_for_update(),
        id=appointment_id
    )

    if appointment.status != "CONFIRMED":
        raise ValidationError("Only CONFIRMED appointments can be checked in.")

    # Compute appointment datetime
    appointment_datetime = datetime.datetime.combine(
        appointment.slot.date,
        appointment.slot.start_time
    )
    appointment_datetime = timezone.make_aware(appointment_datetime)

    allowed_period = appointment_datetime + datetime.timedelta(minutes=15)

    if timezone.now() > allowed_period:
        appointment.status = "NO_SHOW"
        appointment.save()
        raise ValidationError("Patient exceeded 15 minutes. Marked as NO_SHOW.")

    appointment.status = "CHECKED_IN"
    appointment.check_in_time = timezone.now()
    appointment.save()

    return redirect("list_today_appointments")

## done groups and permissions
@login_required
def doctor_queue(request):

    user = request.user

    if not user.groups.filter(name="Doctor").exists():
        raise PermissionDenied("Only doctors are allowed to view the queue.")

    # Filter today's queue for this doctor only
    queue = get_today_queue().filter(doctor=user)

    return render(request, "appointments/doctor_queue.html", {
        "queue": queue
    })

## done groups and permissions
def get_today_queue():
    today = timezone.localdate()

    queue = Appointment.objects.filter(
        slot__date=today,
        status="CHECKED_IN"
    ).select_related(
        "patient",
        "doctor",
        "slot"
    ).order_by(
        "slot__start_time",
        "check_in_time"
    )

    return queue


## done groups and permissions
@login_required
@handle_errors
def receptionist_queue(request):
    user = request.user

    if not user.groups.filter(name="Receptionist").exists():
        raise PermissionDenied("Only receptionists are allowed to view the queue.")

    doctors = User.objects.filter(role='D').order_by('first_name', 'last_name')

    selected_doctor = request.GET.get('doctor', None)

    queue = get_today_queue()

    if selected_doctor:
        queue = queue.filter(doctor__id=selected_doctor)

    context = {
        'queue': queue,
        'doctors': doctors,
        'selected_doctor': selected_doctor,
    }

    return render(request, "appointments/receptionist_queue.html", context)

## done groups and permissions
@login_required
@handle_errors
@transaction.atomic
def call_next_patient(request):

    user = request.user

    if not user.groups.filter(name="Doctor").exists():
        raise PermissionDenied("Only doctors are allowed to call patients.")

    next_patient = get_today_queue().filter(doctor=user).first()

    if not next_patient:
        raise ValidationError("No patients in queue.")

    next_patient.status = "COMPLETED"
    next_patient.save()

    return redirect("doctor_queue")


## done groups and permissions
@login_required
@permission_required("appointments.view_appointment", raise_exception=True)
@handle_errors
def list_patient_appointments(request):

    if not request.user.groups.filter(name="Patient").exists():
        raise PermissionError("Only Patients are allowed to view their appointments.")

    # Filter appointments for this patient
    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related("doctor", "slot").order_by(
        "slot__date", "slot__start_time"
    )

    status_filter = request.GET.get("status")
    if status_filter in ["REQUESTED", "CONFIRMED", "CANCELLED", "COMPLETED", "NO_SHOW"]:
        appointments = appointments.filter(status=status_filter)

    paginator = Paginator(appointments, 7)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "appointments/patient_list.html", {
        "appointments": page_obj,
        "current_status": status_filter
    })

## done groups and permissions
@login_required
@handle_errors
def list_doctor_appointments(request):

    user = request.user

    if not user.groups.filter(name="Doctor").exists():
        raise PermissionDenied("Only Doctors are allowed to view this page.")

    # Base queryset: appointments for this doctor
    appointments = Appointment.objects.filter(
        doctor=user
    ).select_related("patient", "slot")

    # Filters
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

    paginator = Paginator(appointments, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "appointments/doctor_list.html", {
        "appointments": page_obj,
        "current_status": status
    })



@login_required
@handle_errors
def list_today_appointments(request):
    user = request.user

    if not user.groups.filter(name="Receptionist").exists():
       raise PermissionDenied("Only Receptionists are allowed to view today's appointments.")
    
    today = timezone.localdate()
    
    weekday_number = today.weekday()


    appointments = Appointment.objects.filter(
        slot__doctor_schedule__day_of_week=weekday_number
    ).select_related(
        "patient", "doctor", "slot"
    )


    # appointments = Appointment.objects.filter(
    #     slot__date__gte=today
    # ).select_related(
    #     "patient", "doctor", "slot"
    # )

    status = request.GET.get("status")
    doctor = request.GET.get("doctor")
    patient = request.GET.get("patient")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    search = request.GET.get("search")

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

    doctors = User.objects.filter(role='D').order_by('first_name', 'last_name')

    paginator = Paginator(appointments, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "appointments": page_obj,
        "doctors": doctors,
        "selected_doctor": doctor,  # to maintain selection in dropdown
    }

    return render(request, "appointments/receptionist_list_appointments.html", context)

## done groups and permissions
# @login_required
# @handle_errors
# def list_today_appointments(request):

#     user = request.user

#     if not user.groups.filter(name="Receptionist").exists():
#         raise PermissionDenied("Only Receptionists are allowed to view today's appointments.")
    

#     today = timezone.localdate()
#     weekday_number = today.weekday()

#     appointments = Appointment.objects.filter(
#         slot__doctor_schedule__day_of_week=weekday_number
#     ).select_related(
#         "patient", "doctor", "slot"
#     )


#     status = request.GET.get("status")
#     doctor = request.GET.get("doctor")
#     patient = request.GET.get("patient")
#     start_date = request.GET.get("start_date")
#     end_date = request.GET.get("end_date")
#     search = request.GET.get("search")

#     if status:
#         appointments = appointments.filter(status=status)
#     if doctor:
#         appointments = appointments.filter(doctor_id=doctor)
#     if patient:
#         appointments = appointments.filter(patient_id=patient)
#     if start_date:
#         appointments = appointments.filter(slot__date__gte=start_date)
#     if end_date:
#         appointments = appointments.filter(slot__date__lte=end_date)
#     if search:
#         appointments = appointments.filter(
#             Q(id__icontains=search) |
#             Q(patient__first_name__icontains=search) |
#             Q(patient__last_name__icontains=search)
#         )

#     appointments = appointments.order_by("slot__date", "slot__start_time")

#     paginator = Paginator(appointments, 7)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     return render(request, "appointments/receptionist_list_appointments.html", {
#         "appointments": page_obj
#     })

## done groups and permissions
@login_required
@permission_required("appointments.change_appointment", raise_exception=True)
@handle_errors
def show_reschedule_form(request, appointment_id):

    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = request.user

    is_patient = appointment.patient == user and user.groups.filter(name="Patient").exists()
    is_doctor = appointment.doctor == user and user.groups.filter(name="Doctor").exists()
    is_receptionist = user.groups.filter(name="Receptionist").exists()

    if not (is_patient or is_doctor or is_receptionist):
        raise PermissionDenied("You are not allowed to reschedule this appointment.")

    if appointment.status != "REQUESTED":
        raise ValidationError("Only REQUESTED appointments can be rescheduled.")

    today = timezone.localdate()
    now_time = timezone.localtime().time()

    # Fetch available slots for the same doctor, excluding current slot
    available_slots = Slot.objects.filter(
        is_available=True,
        doctor_schedule__doctor=appointment.doctor
    ).filter(
        Q(date__gt=today) | Q(date=today, start_time__gt=now_time)
    ).exclude(
        id=appointment.slot.id
    ).select_related("doctor_schedule").order_by("date", "start_time")

    paginator = Paginator(available_slots, 10)
    page_number = request.GET.get("page")
    paginated_slots = paginator.get_page(page_number)

    return render(request, "appointments/reschedule.html", {
        "appointment": appointment,
        "slots": paginated_slots
    })