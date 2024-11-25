from django.contrib.auth import get_user_model
from django.db import models

import datetime

from django.shortcuts import render

class Class(models.Model):
    professor_key = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    class_name = models.CharField(max_length=200)
    is_archived = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


class Seating:
    choices = (
        ('FR', "Front Right"),
        ('FM', "Front Middle"),
        ('FL', "Front Left"),
        ('BR', "Back Right"),
        ('BM', "Back Middle"),
        ('BL', "Back Left"),
        ('NA', "None")
    )

class Student(models.Model):
    class_key = models.ForeignKey(Class, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    seating = models.CharField(choices=Seating().choices, default="NA", max_length=3)
    total_calls = models.IntegerField(default=0)
    absent_calls = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)

class StudentRating(models.Model):
    student_key = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    attendance = models.BooleanField(default=True)
    prepared = models.BooleanField(default=True)
    score = models.IntegerField(default=5)