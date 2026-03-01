from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    # path('login/', views.login_user, name='login'),
    # path('logout/', views.logout_user, name='logout'),
    # path('profile/', views.profile, name='profile'),
    # path('profile/edit/', views.edit_profile, name='edit_profile'),
    # path('profile/change-password/', views.change_password, name='change_password'),
]