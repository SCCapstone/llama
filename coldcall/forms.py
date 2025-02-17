
from django.forms import ModelForm, CharField, PasswordInput, TextInput, EmailInput
from django.contrib.auth import get_user_model

class RegisterUserForm(ModelForm):
    password = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        model = get_user_model()
        fields = ["username", "first_name", "last_name", "email", "password"]
        widgets = {
            # trying to make the text bold in register (to look like login)
            'username': TextInput(attrs={'class': 'form-control'}),
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'email': EmailInput(attrs={'class': 'form-control'}),
            'password': PasswordInput(attrs={'class': 'form-control'}),
        }