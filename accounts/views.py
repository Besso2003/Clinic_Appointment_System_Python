from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.

def home_view(request):
    return render(request, 'accounts/home.html')

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