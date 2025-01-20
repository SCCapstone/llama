# helper functions for setting up tests
from django.contrib.auth.models import User
from coldcall.models import *

def init_prof():
    return User.objects.create_user(username="test", password="password", first_name = "John", last_name = "Doe", email="test@example.com")

def init_class(prof):
    return Class.objects.create(professor_key = prof, class_name = "Test101")