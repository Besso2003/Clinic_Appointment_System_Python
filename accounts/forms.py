from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    ALLOWED_ROLES = [
        ('P', 'Patient'),
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
        if commit:
            user.save()
            if role:
                group_name = self._role_to_group(role)
                if group_name:
                    group, _ = Group.objects.get_or_create(name=group_name)
                    user.groups.add(group)
        return user

    def _role_to_group(self, code):
        mapping = {'P': 'Patient', 'D': 'Doctor', 'R': 'Receptionist'} # 'A' removed
        return mapping.get(code)