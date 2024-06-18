from functools import wraps

from django.http import HttpRequest
from django.shortcuts import redirect


def user_required(f):
    @wraps(f)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_user:
            return f(request, *args, **kwargs)

        return redirect('user:login')

    return wrapper
