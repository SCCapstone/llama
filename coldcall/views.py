from django.shortcuts import render
from django.views import generic
from django.views.generic import TemplateView, ListView
from .models import Student, Class
# Create your views here.

class IndexView(generic.TemplateView):
    template_name = "coldcall/index.html"

class HomePageView(ListView):
    model = Student
    template_name = "coldcall/home.html"
    context_object_name = "students"

class StudentRandomizerView(TemplateView):
    template_name = "coldcall/randomizer.html"

class CourseHomePageView(generic.DetailView):
    model = Class
    template_name = "coldcall/course_home.html"
    context_object_name = "course"

class StudentMetricsView(generic.DetailView):
    model = Student
    template_name = "coldcall/student_metrics.html"
    context_object_name = "student"

class AddCourseView(TemplateView):
    template_name = "coldcall/add_course.html"

class AddStudentImportView(TemplateView):
    template_name = "coldcall/add_student_import.html"

class AddStudentManualView(TemplateView):
    template_name = "coldcall/add_student_manual.html"

class EditStudentManualView(generic.DetailView):
    model = Student
    template_name = "coldcall/edit_student_manual.html"

class EditStudentCSVView(generic.DetailView):
    model = Student
    template_name = "coldcall/edit_student_csv.html"