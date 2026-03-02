from django.urls import path
from . import views



urlpatterns = [
    
    path('', views.schedule_list, name='schedule-list'),

    path('create/', views.create_doctor_schedule, name='schedule-create'),

    path('update/<int:pk>/', views.update_doctor_schedule, name='schedule-update'),

    path('delete/<int:pk>/', views.delete_doctor_schedule, name='schedule-delete'),
]
    
    
