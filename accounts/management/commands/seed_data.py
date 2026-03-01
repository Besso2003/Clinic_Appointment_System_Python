from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Seed database with initial users"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Seeding database..."))

        User.objects.all().delete()

        users = [
            # Admin
            {
                "username": "admin",
                "email": "admin@mediflow.com",
                "password": "Admin123!",
                "role": "A",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },

            # Doctors
            {
                "username": "dr_mustafa",
                "email": "mustafa@mediflow.com",
                "first_name": "Mustafa",
                "last_name": "Tarek",
                "password": "Doctor123!",
                "role": "D",
            },
            {
                "username": "dr_yasser",
                "email": "yasser@mediflow.com",
                "first_name": "Ahmed",
                "last_name": "Yasser",
                "password": "Doctor123!",
                "role": "D",
            },

            # Receptionists
            {
                "username": "rec_yassin",
                "email": "yassin@mediflow.com",
                "first_name": "Yassin",
                "last_name": "Ibrahim",
                "password": "Reception123!",
                "role": "R",
            },

            # Patients
            {
                "username": "pat_bassant",
                "email": "bassant@mediflow.com",
                "first_name": "Bassant",
                "last_name": "Mohamed",
                "password": "Patient123!",
                "role": "P",
            },
            {
                "username": "pat_ibrahim",
                "email": "ibrahim@mediflow.com",
                "first_name": "Ibrahim",
                "last_name": "Ali",
                "password": "Patient123!",
                "role": "P",
            },
        ]

        for user_data in users:
            password = user_data.pop("password")
            user = User.objects.create(**user_data)
            user.set_password(password)
            user.save()

            self.stdout.write(self.style.SUCCESS(f"Created user: {user.username}"))

        self.stdout.write(self.style.SUCCESS("Seeding completed!"))