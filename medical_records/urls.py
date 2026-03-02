from django.urls import path
from .views import CreateConsultationRecord, UpdateConsultationRecord, ViewConsultationRecord, PatientMedicalHistory
from .views_debug import consultation_detail_preview, patient_history_preview

urlpatterns = [
    path(
        'create/<int:appointment_id>',
        CreateConsultationRecord.as_view(),
        name='consultation-create'
    ),
    path(
        'update/<int:pk>',
        UpdateConsultationRecord.as_view(),
        name='consultation-update'),
    path(
        'view/<int:pk>',
        ViewConsultationRecord.as_view(),
        name='consultation-view'
    ),
    path(
        'patient/<int:patient_id>',
        PatientMedicalHistory.as_view(),
        name='patient-medical-history'
    ),
    path('preview/consultation/', consultation_detail_preview, name='preview-consultation'),
    path('preview/history/', patient_history_preview, name='preview-history'),
]