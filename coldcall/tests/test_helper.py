# helper functions for setting up tests
from django.contrib.auth.models import User
from coldcall.models import *

PROF_USERNAME = "test"
PROF_PASSWORD = "password"
PROF_NAME = "JOHN"
PROF_LASTNAME = "DOE"
PROF_EMAIL = "test@example.com"

CLASS_NAME = "Test101"

def init_prof():
    return User.objects.create_user(username=PROF_USERNAME, password=PROF_PASSWORD, first_name = PROF_NAME, last_name = PROF_LASTNAME, email=PROF_EMAIL)


def init_class(prof):
    return Class.objects.create(professor_key = prof, class_name = CLASS_NAME)