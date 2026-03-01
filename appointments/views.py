from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Appointment, Slot

# Read about select_for_update()

@login_required
@transaction.atomic
def mark_as_no_show(request, appointment_id):

    if request.user.role != "R":
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