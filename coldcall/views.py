from django.shortcuts import redirect, render
from django.views import View, generic
from django.views.generic import TemplateView, ListView, FormView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from datetime import datetime

from .models import Student, Class, StudentRating
from .forms import RegisterUserForm

import random
import json
import csv

# Create your views here.

#class HomePageView(ListView):
#    model = Student
#    template_name = "coldcall/home.html"
#    context_object_name = "students"

class CreateAccountView(FormView): 
    template_name = "registration/register.html"
    form_class = RegisterUserForm
    success_url = "/accounts/login"

    def form_valid(self, form):
        new_user = form.save(commit=False) # need to hash password first
        new_user.password = make_password(form.cleaned_data["password"])
        new_user.save()
        return super().form_valid(form)


class HomePageView(LoginRequiredMixin, View):
    template_name = "coldcall/home.html"

    # user needs to login first
    login_url = '/accounts/login'

    def get(self, request):
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


#class StudentRandomizerView(TemplateView):
#    template_name = "coldcall/randomizer.html"
#param below changed to View instead of TemplateView
class StudentRandomizerView(LoginRequiredMixin,View):
    template_name = "coldcall/randomizer.html"

    def get(self, request):
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
                    students = Student.objects.filter(class_key=selected_class)
                    # randomly select a student if there are students in the selected class
                    if students.exists():
                        ms = random.choice(students).total_calls # initalize with any student value
                        for s in students:
                           ms = min(s.total_calls-s.absent_calls, ms)
                        ms+=3 # buffer room

                        student = None
                        while student == None:
                            student = random.choice(students)
                            if(student.total_calls-student.absent_calls >= ms):
                                student = None
                        

            except Class.DoesNotExist:
                selected_class = None  # if the class does not exist, reset to None

        # context for rendering the template
        context = {
            'classes': classes,  # all classes for the dropdown
            'selected_class': selected_class,  # currently selected class
            'student': student,  # randomly selected student
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



class CourseHomePageView(LoginRequiredMixin,generic.DetailView):
    model = Class
    template_name = "coldcall/course_home.html"
    context_object_name = "course"

class StudentMetricsView(LoginRequiredMixin,generic.DetailView):
    model = Student
    template_name = "coldcall/student_metrics.html"
    context_object_name = "student"

    # Tempoary fix for the previous get function 
    # Removed the JsonResponse and rendered a template instead to allow the passing of attendance rate and performance
    def get_context_data(self, **kwargs): # kwargs variable allowing us to accept any additional keyword arguemnts
        context = super().get_context_data(**kwargs)
        student = self.object
        attendance_rate = student.calculate_attendance_rate()
        performance = student.performance_summary()
        context['attendance_difference'] = student.total_calls - student.absent_calls
        context['attendance_rate'] = attendance_rate
        context['performance_summary'] = performance
        return context

#    Previous get function is below 
#    def get(self, request, student_id):
#        try:
#            student = Student.objects.get(id=student_id)
#            attendance_rate = student.calculate_attendance_rate()
#            performance = student.performance_summary()
#            return JsonResponse({
#                "attendance_rate": attendance_rate,
#                "performance_summary": performance
#            })
#        except Student.DoesNotExist:
#            return JsonResponse({"error": "Student not found"}, status=404)

class StudentUpdateView(View):  # New
    def post(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            data = json.loads(request.body)

            if "absent_calls" in data:
                student.absent_calls += data["absent_calls"]

            if "total_calls" in data:
                student.total_calls += data["total_calls"]

            if "total_score" in data:
                student.total_score += data["total_score"]

            student.save()
            return JsonResponse({"message": "Student updated successfully"})
        except Student.DoesNotExist:
            return JsonResponse({"error": "Student not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

class AddCourseView(LoginRequiredMixin,TemplateView):
    template_name = "coldcall/add_course.html"

    def post(self,request):
        if(request.user.is_authenticated):
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')

            start_date = None
            end_date = None

            # If start_date_str is non empty, convert it to a date object
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                except ValueError:
                    return HttpResponseBadRequest("Invalid date format. Please use YYYY-MM-DD.")
                
            # If end_date_str is non empty, convert it to a date object
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                except ValueError:
                    return HttpResponseBadRequest("Invalid date format. Please use YYYY-MM-DD.")
            
            # If start_date and end_date are both provided, check if the end date is before the start date
            if start_date and end_date and end_date < start_date:
                error_message = "End date cannot be before start date."
                return render(request, self.template_name, {
                    'error_message': error_message,
                    'name': request.POST.get('name'),
                    'start_date': start_date_str,
                    'end_date': end_date_str,
                })

            Class.objects.create(
                professor_key = request.user,
                class_name = request.POST.get('name'),
                start_date = start_date,
                end_date = end_date,
            )

            return redirect('/')
        else:
            return redirect('/accounts/login') #should never reach this, but fall back to redirect    

class ClassDetailsView(View):  # New view for class details
    def get(self, request, class_id):
        try:
            course = Class.objects.get(id=class_id, professor_key=request.user)
            students = course.student_set.all()
            return JsonResponse({
                "class_name": course.class_name,
                "is_active": course.is_active(),
                "total_students": course.total_students(),
                "students": [{"id": s.id, "name": str(s), "score": s.total_score} for s in students],
            })
        except Class.DoesNotExist:
            return JsonResponse({"error": "Class not found or unauthorized"}, status=404)

class AddStudentImportView(LoginRequiredMixin, TemplateView):
    template_name = "coldcall/add_student_import.html"

    # Added the get function so that we can get the class id before we import the students
    def get(self, request): 
        class_id = request.GET.get('class_id')
        if class_id: 
            selected_class = Class.objects.get(id=class_id)
        else: 
            selected_class = None
        classes = Class.objects.all()
        return render(request, self.template_name, {'classes': classes, 'selected_class': selected_class})
    
    def post(self, request): 
        class_id = request.POST.get('class_id')
        file = request.FILES.get('file')
        
        # Check if the file type is csv
        if not file.name.endswith('.csv'):
            return HttpResponseBadRequest("Invalid file type. Please select a CSV file.")
        
        try:
            selected_class = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return HttpResponseBadRequest("Invalid class ID.")
        
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        # Reading CSV file & gathering student information 
        for row in reader:
            usc_id = row.get('usc_id', '').strip()
            first_name = row.get('first_name', '').strip()
            last_name = row.get('last_name', '').strip()
            seating = row.get('seating', '').strip()
            total_calls = row.get('total_calls', '0').strip()
            absent_calls = row.get('absent_calls', '0').strip()
            total_score = row.get('total_score', '0').strip()

            if not usc_id or not first_name or not last_name:
                continue; # Skip row if field is empty 

            Student.objects.create(
                usc_id = usc_id,
                first_name = first_name, 
                last_name = last_name, 
                class_key = selected_class, 
                seating = seating if seating in ['FR', "Front Right", 'FM', "Front Middle", 'FL', "Front Left", 'BR', "Back Right", 'BM', "Back Middle", 'BL', "Back Left", 'NA', "None"] else 'NA',
                total_calls = int(total_calls) if total_calls.isdigit() else 0, 
                absent_calls = int(absent_calls) if absent_calls.isdigit() else 0, 
                total_score = int(total_score) if total_score.isdigit() else 0 
            )                     

        return redirect('/')

class AddEditStudentManualView(LoginRequiredMixin,TemplateView):
    template_name = "coldcall/addedit_student_manual.html"

     # added this to help get classes for the add new student manual page
    def get(self, request, student_id=None):
        classes = Class.objects.filter(professor_key = request.user)
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            student = None

        return render(request, self.template_name, {'classes': classes, 'student': student})
    
    def post(self, request, student_id=None):
        # made to handle form submission. I was getting errors when submitting add
        # student form
        usc_id = request.POST.get('usc_id').upper()
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        class_key_id = request.POST.get('class_key')
        seating = request.POST.get('seating')
        total_calls = request.POST.get('total_calls', 0)
        absent_calls = request.POST.get('absent_calls', 0)
        total_score = request.POST.get('total_score', 0)

        try:
            class_key = Class.objects.get(id=class_key_id)
        except Class.DoesNotExist:
            return HttpResponseBadRequest("Invalid class ID.")

        # if student_id is provided, update the existing Student instance
        if student_id:
            student = Student.objects.get(id=student_id)
            student.usc_id = usc_id
            student.first_name = first_name
            student.last_name = last_name
            student.class_key = class_key
            student.seating = seating
            student.save()
        # create a new student if no ID is provided
        else:
            Student.objects.create(
                usc_id=usc_id,
                first_name=first_name,
                last_name=last_name,
                class_key=class_key,
                seating=seating,
                total_calls=total_calls,
                absent_calls=absent_calls,
                total_score=total_score,
            )

        # send the user back to home page
        return redirect('/')
    
class FilterStudentsByScoreView(View):
    def get(self, request):
        score_filter = request.GET.get('min_score', 0)
        students = Student.objects.filter(total_score__gte=score_filter)
        
        return JsonResponse([{
            "id": student.id,
            "name": f"{student.first_name} {student.last_name}",
            "score": student.total_score
        } for student in students], safe=False)

class ExportView(View): 
    def get(self, request): 
        return render(request, 'coldcall/export.html')
