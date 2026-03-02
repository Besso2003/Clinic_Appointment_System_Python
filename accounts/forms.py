from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "role", "profile_picture")

    def save(self, commit=True):
        """Persist the user and add them to the appropriate group based on role."""
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
        mapping = {'P': 'Patient', 'D': 'Doctor', 'R': 'Receptionist', 'A': 'Admin'}
        return mapping.get(code)
