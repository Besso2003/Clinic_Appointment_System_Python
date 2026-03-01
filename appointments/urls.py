from django.urls import path
from . import views

urlpatterns = [
    # path("", views.appointment_list, name="appointment_list"),
    path(
        "<int:appointment_id>/no-show/",
        views.mark_as_no_show,
        name="mark_as_no_show"
    ),
    path(
        "<int:appoinmtent_id>/completed/",
        views.mark_as_completed,
        name="mark_as_completed"
    ),
    path(
        "/create/",
        views.create_appointment,
        name="create_appointment"
    ),
    path(
        "/cancel",
        views.cancel_appointment,
        name="cancel_appointment"
        )
]