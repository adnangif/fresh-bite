from django.shortcuts import render

from .models import CoveredCity


def landing_page(request):

    covered_cities: CoveredCity = CoveredCity.objects.all()[:10]
    context = {
        "covered_cities": covered_cities
    }

    return render(request, 'landing/landing.html', context)