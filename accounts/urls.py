from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.patient_register_view, name='register'),
    path('register/staff/', views.staff_register_view, name='staff_register'),
    path('login/', views.login_view.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.view_profile, name='profile'),
    path('staff/', views.manage_staff_view, name='manage_staff'),
    path('staff/edit/<int:staff_id>/', views.view_staff_profile, name='edit_staff'),
    path('staff/delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),
]