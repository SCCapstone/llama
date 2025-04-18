from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.db.models import Case, ExpressionWrapper, F, FloatField, IntegerField, Value, When
from django.db.models.functions import Lower
from django.views import View
from django.views.generic import FormView

from .view_helper import get_template_dir, get_demo_dir
from ..forms import LoginUserForm, RegisterUserForm
from ..models import Student, Class, UserData

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

        UserData.objects.create(user=new_user)
        return super().form_valid(form)

class LoginView(DjangoLoginView):
    template_name = "registration/login.html"
    form_class = LoginUserForm
    success_url = "/"

#Default page upon being logged in, no class selected by default.
class HomePageView(LoginRequiredMixin, View):

    # user needs to login first
    login_url = '/demo/'

    def get(self, request):
        self.template_name = get_template_dir("home", request.is_mobile)
        # get all existing classes to select from dropdown

        #changed to only display logged in user's students and classes
        #classes = Class.objects.all()
        user = request.user
        classes = Class.objects.filter(professor_key=user, is_archived=False)
        students = Student.objects.filter(class_key__professor_key=user)

        seen_onboarding = user.userdata.seen_onboarding
        if(not seen_onboarding):
            user.userdata.seen_onboarding = True
            user.userdata.save()

        # get the id of the selected class
        selected_class_id = request.GET.get('class_id')
        sort_query = request.GET.get('sort', '') # default to empty string
        search_first_name_query = request.GET.get('search_first_name', '') # default to empty string
        search_last_name_query = request.GET.get('search_last_name', '') # default to empty string
        search_usc_id_query = request.GET.get('search_usc_id', '') # default to empty string
        
        # get the students that are in that class
        if selected_class_id:
            selected_class = Class.objects.get(id=selected_class_id)
            if selected_class.professor_key != user:
                # prevent user from viewing information by modifying URL
                students = None
                selected_class = None
            else:             
                students = Student.objects.filter(class_key_id=selected_class_id)

        else: 
            # all classes, limited to classes authenticated user has access to and are not archived
            students = Student.objects.filter(class_key__professor_key=user, class_key__is_archived=False)
            selected_class = None
            
        # Apply sorting
        if students and sort_query:
            if sort_query == "average_score":
                # use model annotation to calculate average, as get_average_calls() can not be used with order_by()

                #first calculate total_calls - absent calls using its own annotation
                students = students.annotate(
                    c = ExpressionWrapper(
                        F('total_calls') - F('absent_calls'), 
                        output_field=IntegerField())
                ) 

                students = students.annotate(
                    avg = Case(
                        #prevent divide by 0, always show these students first
                        When(
                            c__lte=0,
                            then=Value(-1)
                        ),
                        default=(F('total_score')/(F('c'))), #actual average calculation
                        output_field=FloatField()
                    )
                ).order_by('avg') #final sort, ascending
            else:
                students = students.order_by(Lower(sort_query))

        # Apply search filters
        if students and search_first_name_query:
            students = students.filter(first_name__icontains=search_first_name_query)
        if students and search_last_name_query:
            students = students.filter(last_name__icontains=search_last_name_query)
        if students and search_usc_id_query:
            students = students.filter(usc_id__icontains=search_usc_id_query)

        context = {
            'students': students,
            'classes': classes,
            'selected_class': selected_class,
            'sort': sort_query,
            'first_name': search_first_name_query,
            'last_name': search_last_name_query,
            'usc_id': search_usc_id_query,
            'seen_onboarding': not seen_onboarding
        }
        return render(request, self.template_name, context)

#Core functionality, selects a random student from a class to be called on.    
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
                    students = list(Student.objects.filter(class_key=selected_class, dropped=False))
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

        #prevent reading attribute from None if class is empty or invalid (i.e no access)
        if selected_class is None or student is None:
            context = {'classes': classes, 'selected_class': selected_class, 'empty': True, 'id_present': False}
            #only show no class message if a class is selected
            if class_id:
                context['id_present'] = True
            return render(request, self.template_name, context)

        context = {
            'classes': classes,  # all classes for the dropdown
            'selected_class': selected_class,  # currently selected class
            'student': student,  # randomly selected student
            'avg_rating': student.get_average_score(),
            'empty': False,
            'id_present' : True
        }
        return render(request, self.template_name, context)
    
    def post(self, request): 
        data = json.loads(request.body)

        present = True
        prepared = True

        rating = data["rating"]
        if rating == "skip":
            messages.success(request, "Student has been skipped.")
            return JsonResponse({"success": True})
        elif rating == "absent":
            rating = 0
            present = False
        elif rating == "unprepared":
            rating = 0
            prepared = False
        elif rating != 'none':
            rating = int(data["rating"][-1]) #negative indexing to get last character

        student = Student.objects.get(id=data["student_id"])
        if student:
            student.add_rating(is_present = present, is_prepared = prepared, score = rating)
            messages.success(request, f"Rating for {student.first_name} {student.last_name} has been successfully saved.")
            return JsonResponse({"success": True})
        else:
            messages.error(request, "Student not found!")
            return JsonResponse({"success": False, "error": "Student not found!"})

#Profile page for user to view and edit their information
class ProfileView(LoginRequiredMixin, View):
    login_url = '/accounts/login'
    
    def get(self, request):
        self.template_name = get_template_dir("profile", request.is_mobile)
        context = {
            'user': request.user,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
            
        try:
            user.save()
            messages.success(request, "Profile updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating profile: {e}")
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            # Update or create UserData model with the new picture
            user_data, created = UserData.objects.get_or_create(user=user)
            user_data.profile_picture = profile_picture
            user_data.save()
        
        return redirect('profile')
    
class ChangePasswordView(View):
    def post(self, request):
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('password')
        if not check_password(old_password, user.password):
            messages.error(request, "Current password is incorrect!")
            return redirect('profile')
        elif len(new_password) >= 8:
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully!")
            update_session_auth_hash(request, user)
            return redirect('profile')
        else:
            messages.error(request, "Password must be at least 8 characters long!")
            return redirect('profile')
        
class DemoView(View):
    def get(self, request):
        self.template_name = get_demo_dir()
        return render(request, self.template_name)