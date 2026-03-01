from django.urls import path
from . import views

urlpatterns = [
    # path("", views.appointment_list, name="appointment_list"),
    path(
        "<int:appointment_id>/no-show/",
        views.mark_as_no_show,
        name="mark_as_no_show"
    ),
]