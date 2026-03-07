from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.forms import StaffRegistrationForm, PatientRegistrationForm
from django.contrib.auth.models import Group

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
                "password": "Maher123!",
                "role": "A",
                "first_name": "Admin",
                "last_name": "User",
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

            if user_data.get("role") == "A":
                user = User.objects.create_superuser(
                    username=user_data["username"],
                    email=user_data["email"],
                    password=password,
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role="A"
                )
                group, _ = Group.objects.get_or_create(name='Admin')
                user.groups.add(group)
                user.save()
                group_names = list(user.groups.values_list('name', flat=True))
                primary_group = group_names[0] if group_names else None
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.username} (group: {primary_group})"))
                continue

            form_data = {
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'email': user_data.get('email'),
                'role': user_data.get('role'),
                'password1': password,
                'password2': password,
            }

            if user_data.get("role") == "P":
                form = PatientRegistrationForm(form_data)
            else:
                form = StaffRegistrationForm(form_data)

            if form.is_valid():
                user = form.save()
                group_names = list(user.groups.values_list('name', flat=True))
                primary_group = group_names[0] if group_names else None
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.username} (group: {primary_group})"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to create {user_data.get('username')}: {form.errors}"))

        self.stdout.write(self.style.SUCCESS("Seeding completed!"))