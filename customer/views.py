from django.http import HttpRequest
from django.shortcuts import render


def hello_world(request: HttpRequest):
    return render(request, 'customer/hello_world.html')

