from django.shortcuts import redirect
from functools import wraps
from django.http import HttpResponse, HttpResponseForbidden

def role_required(allowed_roles):
    """Return a message if user is not allowed instead of redirecting."""
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponse("You must be logged in to access this page.", status=401)
            if request.user.role not in allowed_roles:
                return HttpResponse(
                    f"Access denied. Your role cannot access this page.",
                    status=403
                )
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator