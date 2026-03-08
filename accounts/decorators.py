from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def admin_required(view_func):
    """
    Decorator for views that allows only logged-in admins.
    """
    @login_required  
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'A': 
            return HttpResponseForbidden("You are not allowed to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper