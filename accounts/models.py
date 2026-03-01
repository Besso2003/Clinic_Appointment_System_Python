from django.contrib.auth.models import AbstractUser
from django.db import models

# AbstractUser default fields: username, password, email, first_name, last_name, is_staff, and is_active.
class User(AbstractUser):
    ROLE_CHOICES = [
        ('P', 'Patient'),
        ('D', 'Doctor'),
        ('R', 'Receptionist'),
        ('A', 'Admin'),
    ]
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='P')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
        # self.get_role_display() is a method provided by Django for fields with choices. It returns the name of the current choice.