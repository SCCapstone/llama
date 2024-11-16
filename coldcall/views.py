from django.shortcuts import redirect, render
from django.views import View, generic
from django.views.generic import TemplateView, ListView
from .models import Student, Class
from django.contrib.auth.mixins import LoginRequiredMixin
import random
# Create your views here.

class IndexView(generic.TemplateView):
    template_name = "coldcall/index.html"

#class HomePageView(ListView):
#    model = Student
#    template_name = "coldcall/home.html"
#    context_object_name = "students"

class HomePageView(LoginRequiredMixin, View):
    template_name = "coldcall/home.html"

    # user needs to login first
    login_url = '/accounts/login'

    def get(self, request):
        # get all existing classes to select from dropdown

        #changed to only display logged in user's students and classes
        #classes = Class.objects.all()

        classes = Class.objects.filter(professor_key=request.user)
        students = Student.objects.filter(class_key__professor_key=request.user)

        # get the id of the selected class
        # WAITING UNTIL TEAMMATES SAY IF WE NEED A LOGIN - CADE
        selected_class_id = request.GET.get('class_id')

        # get the students that are in that class
        if selected_class_id:
            students = Student.objects.filter(class_key_id=selected_class_id)
            selected_class = Class.objects.get(id=selected_class_id)
        else:
            students = Student.objects.all()
            selected_class = None

        context = {
            'students': students,
            'classes': classes,
            'selected_class': selected_class,
        }
        return render(request, self.template_name, context)

#class StudentRandomizerView(TemplateView):
#    template_name = "coldcall/randomizer.html"
#param below changed to View instead of TemplateView
class StudentRandomizerView(LoginRequiredMixin,View):
    template_name = "coldcall/randomizer.html"

    def get(self, request):
        # get all classes to populate the dropdown
        classes = Class.objects.all()
        class_id = request.GET.get('class_id')  # selected class ID from query parameters

        # initialize variables for the selected class and student
        student = None
        selected_class = None

        # check if a class ID is provided in the query parameters
        if class_id:
            try:
                # get the selected class and filter students by this class
                selected_class = Class.objects.get(id=class_id)
                students = Student.objects.filter(class_key=selected_class)

                # randomly select a student if there are students in the selected class
                if students.exists():
                    student = random.choice(students)
            except Class.DoesNotExist:
                selected_class = None  # if the class does not exist, reset to None

        # context for rendering the template
        context = {
            'classes': classes,  # all classes for the dropdown
            'selected_class': selected_class,  # currently selected class
            'student': student,  # randomly selected student
        }
        return render(request, self.template_name, context)


class CourseHomePageView(LoginRequiredMixin,generic.DetailView):
    model = Class
    template_name = "coldcall/course_home.html"
    context_object_name = "course"

class StudentMetricsView(LoginRequiredMixin,generic.DetailView):
    model = Student
    template_name = "coldcall/student_metrics.html"
    context_object_name = "student"

class AddCourseView(LoginRequiredMixin,TemplateView):
    template_name = "coldcall/add_course.html"

    def post(self,request):
        if(request.user.is_authenticated):
            Class.objects.create(
                professor_key = request.user,
                class_name = request.POST.get('name')
            )
            return redirect('/')
        else:
            return redirect('accounts/login') #should never reach this, but fall back to redirect


class AddStudentImportView(LoginRequiredMixin,TemplateView):
    template_name = "coldcall/add_student_import.html"

class AddStudentManualView(LoginRequiredMixin,TemplateView):
    template_name = "coldcall/add_student_manual.html"

     # added this to help get classes for the add new student manual page
    def get(self, request):
        classes = Class.objects.all()
        return render(request, self.template_name, {'classes': classes})
    
    def post(self, request):
        # made to handle form submission. I was getting errors when submitting add
        # student form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        class_key_id = request.POST.get('class_key')
        seating = request.POST.get('seating')
        total_calls = request.POST.get('total_calls', 0)
        absent_calls = request.POST.get('absent_calls', 0)
        total_score = request.POST.get('total_score', 0)

        # Create and save the new Student instance
        Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            class_key=Class.objects.get(id=class_key_id),
            seating=seating,
            total_calls=total_calls,
            absent_calls=absent_calls,
            total_score=total_score,
        )

        # send the user back to home page
        return redirect('coldcall:home')

class EditStudentManualView(LoginRequiredMixin,generic.DetailView):
    model = Student
    template_name = "coldcall/edit_student_manual.html"

class EditStudentCSVView(LoginRequiredMixin,generic.DetailView):
    model = Student
    template_name = "coldcall/edit_student_csv.html"