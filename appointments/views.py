from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from .models import Appointment
# Temporary until DB models are ready

appointments = [
    {
        "id": 1,
        "patient_id": 101,
        "doctor_id": 201,
        "date": "2026-03-01",
        "time": "10:00 AM"
    },
    {
        "id": 2,
        "patient_id": 102,
        "doctor_id": 201,
        "date": "2026-03-01",
        "time": "11:00 AM"
    },
    {
        "id": 3,
        "patient_id": 101,
        "doctor_id": 202,
        "date": "2026-03-02",
        "time": "02:00 PM"
    }
]


def appointment_list(request):

    result = ""

    for appointment in appointments:
        result += (
            f"ID: {appointment['id']} | "
            f"Patient ID: {appointment['patient_id']} | "
            f"Doctor ID: {appointment['doctor_id']} | "
            f"Date: {appointment['date']} | "
            f"Time: {appointment['time']}\n"
        )

    return HttpResponse(result)

# Would uncomment this when auth and other models are ready

# @login_required
# def appointment_list(request):
    # user = request.user

    # We need to use groups instead of role

    # if user.role == "Receptionist":
    #     appointments = Appointment.objects.all()

    # elif user.role == "Patient":
    #     appointments = Appointment.objects.filter(patient=user)

    # elif user.role == "Doctor":
    #     appointments = Appointment.objects.filter(doctor=user)

    # else:
    #     appointments = Appointment.objects.none() 

    # appointments = appointments.objects.all().select_related("patient", "doctor", "slot")

    # result = ""

    # for appointment in appointments:
    #     result += (
    #         f"ID: {appointment.id} | "
    #         f"Patient: {appointment.patient.username} | "
    #         f"Doctor: {appointment.doctor.username} | "
    #         f"Status: {appointment.status}\n"
    #     )

    # return HttpResponse(result)

    # return render(request, "appointments/appointment_list.html", {
    #     "appointments": appointments
    # })