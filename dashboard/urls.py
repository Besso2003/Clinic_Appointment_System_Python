from django.urls import path
from . import views

urlpatterns = [
	path('admin/', views.admin_dashboard, name='admin'),
	path('doctor/', views.doctor_dashboard, name='doctor'),
	path('receptionist/', views.receptionist_dashboard, name='receptionist'),
	path('patient/', views.patient_dashboard, name='patient'),
]