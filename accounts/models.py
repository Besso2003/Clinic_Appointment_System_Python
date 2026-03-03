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

    role = models.CharField(
        max_length=1,
        choices=ROLE_CHOICES,
        default='P',
        help_text='User role within the clinic system.',
    )

    email = models.EmailField(
        unique=True, 
        blank=False, 
        null=False,
        error_messages={
            'unique': "A user with that email already exists.",
        }
    )
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return f"{self.username}"