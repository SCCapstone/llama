from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView, TemplateView

from .view_helper import get_template_dir
from ..models import Class
from datetime import datetime

#Allows the user to add a new empty class with a name and dates.
class AddCourseView(LoginRequiredMixin,TemplateView):
    def get(self, request):
        self.template_name = get_template_dir("add_course", request.is_mobile)
        return render(request, self.template_name)

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

#TODO: This is unused, where is it intended for?
class ClassDetailsView(View):
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

#Extension of home page when a class is selected.
class CourseHomePageView(LoginRequiredMixin,DetailView):
    model = Class
    context_object_name = "course"
    def get(self, request):
        self.template_name = get_template_dir("course_home", request.is_mobile)