from django.shortcuts import get_object_or_404, render, redirect
from .forms import StaffRegistrationForm, PatientRegistrationForm, User, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.contrib.auth import update_session_auth_hash
# Create your views here.

def home_view(request):
    return render(request, 'accounts/home.html')


# LoginView handles:authentication, password validation, session creation
class login_view(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user
    # reverse_lazy delays the URL resolution until runtime, when the view is actually called
        if user.role == 'A':
            return reverse_lazy('admin_analytics')
        elif user.role == 'D':  
            return reverse_lazy('doctor')
        elif user.role == 'R': 
            return reverse_lazy('receptionist')
        elif user.role == 'P':
            return reverse_lazy('patient')
        else:
            return reverse_lazy('home')

@admin_required
def staff_register_view(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def patient_register_view(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def view_profile(request):
    user = request.user

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            # Keep the user logged in after password change
            password = form.cleaned_data.get("password1")
            if password:
                update_session_auth_hash(request, user)
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=user)

    # Compute dashboard URL for Home button
    if user.role == 'A':
        dashboard_url = reverse('admin')
    elif user.role == 'D':
        dashboard_url = reverse('doctor')
    elif user.role == 'R':
        dashboard_url = reverse('receptionist')
    else:
        dashboard_url = reverse('patient')

    return render(request, "accounts/profile.html", {
        "form": form,
        "dashboard_url": dashboard_url
    })
    
    
@admin_required
def manage_staff_view(request):
    staff_list = User.objects.filter(role__in=['A', 'D', 'R']).order_by('last_name')
    
    return render(request, 'dashboard/manage_staff.html', {
        'staff_list': staff_list
    })

@admin_required
def delete_staff(request, staff_id):
    if request.user.role != 'A' or request.method != 'POST':
        return redirect('manage_staff')

    staff_member = get_object_or_404(User, id=staff_id)
    
    if staff_member == request.user:
        messages.error(request, "You cannot delete your own account.")
    else:
        staff_member.delete()
        messages.success(request, "Staff member deleted successfully.")
        
    return redirect('manage_staff')

@admin_required
def view_staff_profile(request, staff_id):        
    user_to_edit = get_object_or_404(User, id=staff_id)
    
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        profile_picture = request.FILES.get("profile_picture")

        user_to_edit.first_name = first_name
        user_to_edit.last_name = last_name
        user_to_edit.email = email
        user_to_edit.username = username
        
        if profile_picture:
            user_to_edit.profile_picture = profile_picture

        user_to_edit.save()
        messages.success(request, f"Profile for {user_to_edit.username} updated successfully!")
        
        return redirect("manage_staff") 

    return render(request, "dashboard/staff_profile.html", {"user": user_to_edit})