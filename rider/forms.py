from django.forms import ModelForm

from modelapp.models import Rider


class UpdateRiderForm(ModelForm):
    class Meta:
        model = Rider
        fields = ['first_name', 'last_name', 'email', 'phone']