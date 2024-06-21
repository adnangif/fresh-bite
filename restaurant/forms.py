from django.forms import ModelForm

from modelapp.models import Restaurant


class RestaurantForm(ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'phone', 'phone2', 'opens_at', 'closes_at']
