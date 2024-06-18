from functools import wraps

from django.http import HttpRequest
from django.shortcuts import redirect


def owner_required(f):
    @wraps(f)
    def wrap(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_restaurant_owner:
            return f(request, *args, **kwargs)

        return redirect('restaurant:login')

    return wrap
