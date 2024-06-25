
from django.forms import ModelForm

from modelapp.models import User


class UpdateUserForm(ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']