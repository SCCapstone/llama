
from django.forms import ModelForm, CharField, PasswordInput
from django.contrib.auth import get_user_model

class RegisterUserForm(ModelForm):
    password = CharField(widget=PasswordInput())
    class Meta:
        model = get_user_model()
        fields = ["username", "first_name", "last_name", "email", "password"]