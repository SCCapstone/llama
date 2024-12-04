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
    def is_active(self):  
        today = datetime.date.today()
        if self.start_date and self.end_date:
            return self.start_date <= today <= self.end_date
        return not self.is_archived

    def total_students(self):  
        return self.student_set.count()

    def get_student_performance(self):  # Returns students with their performance (score and attendance)
        students = self.student_set.all()
        performance_data = [{
            "student_name": f"{student.first_name} {student.last_name}",
            "score": student.total_score,
            "attendance_rate": (student.total_calls - student.absent_calls) / student.total_calls * 100 if student.total_calls else 0
        } for student in students]
        return performance_data

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
    def calculate_attendance_rate(self):
        if self.total_calls == 0:
            return 0
        return ((self.total_calls - self.absent_calls)/self.total_calls) * 100
    
    def performance_summary(self):
        attendance_rate = self.calculate_attendance_rate()
        if attendance_rate > 90:
            return "Excellent"
        elif attendance_rate > 75:
            return "Good"
        else:
            return "Needs Improvemnet"

    def attendance_details(self):  # Returns detailed attendance info for a student
        attendance_rate = self.calculate_attendance_rate()
        return {
            "attendance_rate": attendance_rate,
            "absent_calls": self.absent_calls,
            "total_calls": self.total_calls,
        }
    
class StudentRating(models.Model):
    student_key = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    attendance = models.BooleanField(default=True)
    prepared = models.BooleanField(default=True)
    score = models.IntegerField(default=5)
