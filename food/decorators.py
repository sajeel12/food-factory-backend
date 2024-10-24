from django.shortcuts import redirect
from functools import wraps
from django.core.exceptions import PermissionDenied

def group_required(group_name, redirect_url=None):
    """
    Custom decorator to restrict access to a view based on group membership.
    If the user is not in the required group:
    - Redirects to the specified URL if provided.
    - Raises PermissionDenied if no redirect_url is given.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:  # Check if the user is logged in
                return redirect('login')  # Redirect to login page if not authenticated

            # Check if the user is in the specified group
            if not request.user.groups.filter(name=group_name).exists():
                if redirect_url:
                    return redirect(redirect_url)  # Redirect to the specified URL
                else:
                    raise PermissionDenied  # Raise 403 error if no redirect URL

            # If the user is in the group, proceed to the view
            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator
