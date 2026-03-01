from django.urls import path
from .views import CreateConsultationRecord

urlpatterns = [
    path(
        'create/<int:appointment_id>',
        CreateConsultationRecord.as_view(),
        name='consultation-create'
    ),
]