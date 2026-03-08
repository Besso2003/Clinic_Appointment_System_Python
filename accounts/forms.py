from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

User = get_user_model()

# inherit from UserCreationForm because it provides:
# password fields (password1 and password2) and validation for matching passwords.
# password hashing		
# user creation logic

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

class ProfileUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'id': 'password1'}),
        required=False,
        help_text="Leave blank if you don't want to change it."
    )
    password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'id': 'password2'}),
        required=False
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'id': 'profileInput'})
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "profile_picture"]
        widgets = {
            'first_name': forms.TextInput(attrs={'id': 'first_name'}),
            'last_name': forms.TextInput(attrs={'id': 'last_name'}),
            'email': forms.EmailInput(attrs={'id': 'email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:  # if either is filled
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)  # hashes password correctly
        if commit:
            user.save()
        return user