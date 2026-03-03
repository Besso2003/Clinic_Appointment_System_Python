from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
# Create your views here.

def home_view(request):
    return render(request, 'accounts/home.html')


class login_view(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user

        if user.role == 'A':
            return reverse_lazy('admin')
        elif user.role == 'D':  
            return reverse_lazy('doctor')
        elif user.role == 'R': 
            return reverse_lazy('receptionist')
        elif user.role == 'P':
            return reverse_lazy('patient')
        else:
            return reverse_lazy('home')


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def view_profile(request):
    user = request.user 
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        profile_picture = request.FILES.get("profile_picture")

        # Update fields
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        if profile_picture:
            user.profile_picture = profile_picture

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile") 

    return render(request, "accounts/profile.html", {"user": user})