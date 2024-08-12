from datetime import timedelta, datetime
from django.utils import timezone

from django.http import HttpResponse
from django.shortcuts import render, redirect

from modelapp.models import PasswordReset, Person
from .models import CoveredCity
from modelapp.managers import Roles


def landing_page(request):
    print(request.user)

    covered_cities: CoveredCity = CoveredCity.objects.all()[:10]
    context = {
        "covered_cities": covered_cities,
        "roles": Roles,
    }

    return render(request, 'landing/landing.html', context)


def reset_password(request, reset_id):
    reset_obj: PasswordReset = PasswordReset.objects.filter(
        last_update__gt=timezone.now() - timedelta(minutes=5),
        reset_token=reset_id
    ).last()

    if not reset_obj:
        return HttpResponse(status=404)

    if request.method == 'POST':
        password = request.POST.get('password')
        reset_obj.person.set_password(password)
        reset_obj.person.save()
        reset_obj.delete()
        return redirect('user:login')

    context = {
        'reset_id': reset_id,
        'person': reset_obj.person,
    }
    return render(request, 'landing/reset-password.html', context)


def request_reset_password(request):
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        person:Person = Person.objects.filter(email__iexact=email).last()
        if person:
            person.send_password_reset_email()
            return render(request, 'landing/password-reset-request-successful.html')

        context['error'] = "Email Not Found"

    return render(request, 'landing/reqeust-reset-password.html', context)
