from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.forms import UserRegistrationForm

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
            # use the registration form so password handling and validation are centralized
            password = user_data.pop("password")

            form_data = {
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'email': user_data.get('email'),
                'role': user_data.get('role'),
                'password1': password,
                'password2': password,
            }

            form = UserRegistrationForm(form_data)
            if form.is_valid():
                # save user and let the form attach the proper group
                user = form.save()

                # apply optional flags that aren't exposed on the form
                if 'is_staff' in user_data:
                    user.is_staff = user_data.get('is_staff')
                if 'is_superuser' in user_data:
                    user.is_superuser = user_data.get('is_superuser')
                user.save()

                # report created user and primary group (if any)
                group_names = list(user.groups.values_list('name', flat=True))
                primary_group = group_names[0] if group_names else None
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.username} (group: {primary_group})"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to create {user_data.get('username')}: {form.errors}"))

        self.stdout.write(self.style.SUCCESS("Seeding completed!"))