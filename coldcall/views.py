from django.shortcuts import redirect, render
from django.views import View, generic
from django.views.generic import TemplateView, ListView
from .models import Student, Class
# Create your views here.

class IndexView(generic.TemplateView):
    template_name = "coldcall/index.html"

#class HomePageView(ListView):
#    model = Student
#    template_name = "coldcall/home.html"
#    context_object_name = "students"

class HomePageView(View):
    template_name = "coldcall/home.html"

    def get(self, request):
        # get all existing classes to select from dropdown
        classes = Class.objects.all()

        # get the id of the selected class
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

class EditStudentManualView(generic.DetailView):
    model = Student
    template_name = "coldcall/edit_student_manual.html"

class EditStudentCSVView(generic.DetailView):
    model = Student
    template_name = "coldcall/edit_student_csv.html"