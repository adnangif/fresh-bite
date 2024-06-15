from django.shortcuts import render

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