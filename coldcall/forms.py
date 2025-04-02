
from django.forms import ModelForm, CharField, PasswordInput, TextInput, EmailInput
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3, ReCaptchaV2Checkbox

class RegisterUserForm(ModelForm):
    password = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={'class': 'form-control'}, required_score=0.85))

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
            'captcha': ReCaptchaField(widget=ReCaptchaV3(attrs={'class': 'form-control'}, required_score=0.85))

        }

class LoginUserForm(AuthenticationForm):
    username = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    password = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={'class': 'form-control'}, required_score=0.85))

    class Meta:
        model = get_user_model()
        fields = ["username", "password", "captcha"]