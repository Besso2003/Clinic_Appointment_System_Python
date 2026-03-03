from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

User = get_user_model()

class StaffRegistrationForm(UserCreationForm):
    ALLOWED_ROLES = [
        ('A', 'Admin'),
        ('D', 'Doctor'),
        ('R', 'Receptionist'),
    ]
    role = forms.ChoiceField(choices=ALLOWED_ROLES, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "role", "profile_picture")

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        user.is_staff = True 
        if commit:
            user.save()
            group_name = {'D': 'Doctor', 'R': 'Receptionist', 'A': 'Admin'}.get(role)
            if group_name:
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
        return user


class PatientRegistrationForm(UserCreationForm):    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "profile_picture")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'P' 
        if commit:
            user.save()
            group, _ = Group.objects.get_or_create(name='Patient')
            user.groups.add(group)
        return user