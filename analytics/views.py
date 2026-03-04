from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.db.models.functions import ExtractHour
from appointments.models import Appointment
from scheduling.models import Slot


class AdminAnalytics(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "analytics/admin_analytics.html"

    # Only allow admins
    def test_func(self):
        return self.request.user.role == 'A'

    def handle_no_permission(self):
        from django.shortcuts import redirect
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_appointments = Appointment.objects.count()
        completed = Appointment.objects.filter(status="COMPLETED").count()
        no_show = Appointment.objects.filter(status="NO_SHOW").count()

        completion_rate = (completed / total_appointments * 100) if total_appointments else 0
        no_show_rate = (no_show / total_appointments * 100) if total_appointments else 0

        total_slots = Slot.objects.count()
        booked_slots = Slot.objects.filter(is_available=False).count()
        utilization_rate = (booked_slots / total_slots * 100) if total_slots else 0

        peak_hours = (
            Appointment.objects
            .annotate(hour=ExtractHour("slot__start_time"))
            .values("hour")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        doctor_stats = (
            Appointment.objects
            .values("doctor__first_name", "doctor__last_name")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        context.update({
            "total_appointments": total_appointments,
            "completion_rate": round(completion_rate, 1),
            "no_show_rate": round(no_show_rate, 1),
            "utilization_rate": round(utilization_rate, 1),
            "peak_hours": peak_hours,
            "doctor_stats": doctor_stats,
        })

        return context