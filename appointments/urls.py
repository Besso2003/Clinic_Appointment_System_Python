from django.urls import path
from . import views

urlpatterns = [
    # path("", views.appointment_list, name="appointment_list"),
    path("<int:appointment_id>/no-show/", views.mark_as_no_show, name="mark_as_no_show"),
    path("<int:appointment_id>/completed/", views.mark_as_completed, name="mark_as_completed"),
    path("create/<int:slot_id>/", views.create_appointment, name="create_appointment"),
    path("<int:appointment_id>/cancel/", views.cancel_appointment, name="cancel_appointment"),

    # Form to show available slots and doctors
    path("create/", views.show_create_appointment_form, name="show_create_appointment_form"),

    path('generate_slots/<int:schedule_id>/', views.generate_slots_view, name='generate_slots'),

    path('my-appointments/', views.list_patient_appointments, name='list_patient_appointments'),
]