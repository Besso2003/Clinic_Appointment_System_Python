from django.urls import path
from .views import CreateConsultationRecord, UpdateConsultationRecord

urlpatterns = [
    path(
        'create/<int:appointment_id>',
        CreateConsultationRecord.as_view(),
        name='consultation-create'
    ),
    path('update/<int:pk>',
        UpdateConsultationRecord.as_view(),
        name='consultation-update'),
]