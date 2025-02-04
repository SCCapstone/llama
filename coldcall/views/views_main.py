
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import FormView

from .view_helper import get_template_dir
from ..forms import RegisterUserForm
from ..models import Student, Class

import json, random

#Registration page using custom form
class CreateAccountView(FormView): 
    template_name = "registration/register.html"
    form_class = RegisterUserForm
    success_url = "/accounts/login"

    def form_valid(self, form):
        new_user = form.save(commit=False) # need to hash password first
        new_user.password = make_password(form.cleaned_data["password"])
        new_user.save()
        return super().form_valid(form)

#Default page upon being logged in, no class selected by default.
class HomePageView(LoginRequiredMixin, View):

    # user needs to login first
    login_url = '/accounts/login'

    def get(self, request):
        self.template_name = get_template_dir("home", request.is_mobile)
        # get all existing classes to select from dropdown

        #changed to only display logged in user's students and classes
        #classes = Class.objects.all()

        classes = Class.objects.filter(professor_key=request.user, is_archived=False)
        students = Student.objects.filter(class_key__professor_key=request.user)

        # get the id of the selected class
        # WAITING UNTIL TEAMMATES SAY IF WE NEED A LOGIN - CADE
        selected_class_id = request.GET.get('class_id')

        # get the students that are in that class
        if selected_class_id:
            selected_class = Class.objects.get(id=selected_class_id)
            if selected_class.professor_key != request.user:
                # prevent user from viewing information by modifying URL
                students = None
                selected_class = None
            else:             
                students = Student.objects.filter(class_key_id=selected_class_id)

        else: 
            # all classes, limited to classes authenticated user has access to and are not archived
            students = Student.objects.filter(class_key__professor_key=request.user, class_key__is_archived=False)
            selected_class = None

        context = {
            'students': students,
            'classes': classes,
            'selected_class': selected_class,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Archive a class
        class_id = request.POST.get('class_id')
        if class_id:
            try:
                class_to_archive = Class.objects.get(id=class_id)
                class_to_archive.is_archived = True
                class_to_archive.save()
            except Class.DoesNotExist:
                #TODO handle this error
                pass

        return redirect('home')

#Core functionality, selects a random student from a course to be called on.    
class StudentRandomizerView(LoginRequiredMixin,View):

    def get(self, request):
        self.template_name = get_template_dir("randomizer", request.is_mobile)
        # get all classes to populate the dropdown
        classes = Class.objects.filter(professor_key = request.user)
        class_id = request.GET.get('class_id')  # selected class ID from query parameters

        # initialize variables for the selected class and student
        student = None
        selected_class = None

        # check if a class ID is provided in the query parameters
        if class_id:
            try:
                # get the selected class and filter students by this class
                selected_class = Class.objects.get(id=class_id)
                
                #hide information on class without access
                if selected_class.professor_key != request.user:
                    selected_class = None
                else: 
                    students = list(Student.objects.filter(class_key=selected_class))
                    # randomly select a student if there are students in the selected class
                    if students:
                        # set maximum calls requirement to 3 higher than the lowest in the class 
                        ms = min((s.total_calls - s.absent_calls) for s in students) + 3
                        student = None
                        while student == None:
                            student = random.choice(students)
                            if(student.total_calls-student.absent_calls >= ms):
                                students.remove(student)
                                student = None
                        

            except Class.DoesNotExist:
                selected_class = None  # if the class does not exist, reset to None

        # context for rendering the template
        context = {
            'classes': classes,  # all classes for the dropdown
            'selected_class': selected_class,  # currently selected class
            'student': student,  # randomly selected student
            'avg_rating': student.get_average_score()
        }
        return render(request, self.template_name, context)
    
    def post(self, request): 
        data = json.loads(request.body)
        rating = -1 # default rating for absent/unprepared w/ no star chosen
        if data["rating"] != 'none':
            rating = int(data["rating"][-1]) #negative indexing to get last character

        student = Student.objects.get(id=data["student_id"])
        if student:
            student.add_rating(is_present = not data["is_absent"], is_prepared = not data["is_unprepared"], score = rating)
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Student not found!"})