from django.urls import path
from . import views

app_name = 'rider'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('track-orders/', views.track_orders, name='track_orders'),
]