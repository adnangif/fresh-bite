from django.urls import path
from . import views

app_name = 'landingapp'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('reset/<str:reset_id>/', views.reset_password, name='reset_password'),
    path('request-reset/', views.request_reset_password, name='request_reset_password'),
]