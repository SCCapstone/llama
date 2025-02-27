from django.contrib.auth import get_user_model
from django.db import models

import datetime
from  django.utils import timezone

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
    usc_id = models.CharField(max_length=9, null=True)
    email = models.EmailField(max_length=100, null = True) 
    class_key = models.ForeignKey(Class, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    seating = models.CharField(choices=Seating().choices, default="NA", max_length=3)
    total_calls = models.IntegerField(default=0)
    absent_calls = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)

    def add_rating(self, score, is_present=True, is_prepared=True, in_date=None):
        if in_date is None:
            in_date = timezone.now() # default value locks time on server start
        new_rating = StudentRating(student_key = self, attendance = is_present, prepared = is_prepared, score = score, date = in_date)
        new_rating.save()
        self.recalculate_all()
        pass
    
    def calculate_attendance_rate(self):
        if self.total_calls == 0:
            return 0
        return round(((self.total_calls - self.absent_calls)/self.total_calls) * 100, 2)
    
    def get_average_score(self):
        if self.total_calls - self.absent_calls <= 0:
            return 0
        return round(self.total_score/(self.total_calls-self.absent_calls), 2)
    
    def performance_summary(self):
        attendance_rate = self.calculate_attendance_rate()
        if attendance_rate > 90:
            return "Excellent"
        elif attendance_rate > 75:
            return "Good"
        else:
            return "Needs Improvement"
        
    def recalculate_all(self):
        self.recalculate_total_calls()
        self.recalculate_absent_calls()
        self.recalculate_total_score()
        return self
        
    def recalculate_total_calls(self):
        self.total_calls = len(StudentRating.objects.filter(student_key = self))
        self.save()
        return self.total_calls
    
    def recalculate_absent_calls(self):
        self.absent_calls = len(StudentRating.objects.filter(student_key = self, attendance = False))
        self.save()
        return self.absent_calls
    
    def recalculate_total_score(self):
        self.total_score = sum(s.score for s in StudentRating.objects.filter(student_key = self, attendance = True))
        self.save()
        return self.total_score

#    def attendance_details(self):  # Returns detailed attendance info for a student
#        attendance_rate = self.calculate_attendance_rate()
#        return {
#            "attendance_rate": attendance_rate,
#            "absent_calls": self.absent_calls,
#            "total_calls": self.total_calls,
#        }
    
class StudentRating(models.Model):
    student_key = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    attendance = models.BooleanField(default=True)
    prepared = models.BooleanField(default=True)
    score = models.IntegerField(default=5)

    #used in student's table view
    def get_formatted_rating(self):
        if not self.attendance:
            return "❗ Absent"
        return str(self.score) + "⭐" + ("⚠️" if not self.prepared else "")

# helper data model containing additional information related to users
class UserData(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    seen_onboarding = models.BooleanField(default=False)