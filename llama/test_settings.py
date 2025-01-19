from .settings import *

PASSWORD_HASHERS = (
    "django.contrib.auth.hashers.MD5PasswordHasher", #use less secure hash for faster tests
)