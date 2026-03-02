from django.urls import path
from .views import CreateConsultationRecord, UpdateConsultationRecord, ViewConsultationRecord

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
        'view/<int:pk>/',
        ViewConsultationRecord.as_view(),
        name='consultation-view'
    ),
]