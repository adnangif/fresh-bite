from django.forms import ModelForm

from modelapp.models import Restaurant, MenuItem


class RestaurantForm(ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'phone', 'phone2', 'opens_at', 'closes_at']


class UpdateMenuItemForm(ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'price', 'description', 'image']
