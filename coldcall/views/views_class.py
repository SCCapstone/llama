from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView, TemplateView

from .view_helper import get_template_dir
from ..models import Class
from datetime import datetime

#Allows the user to add a new empty class with a name and dates.
class AddClassView(LoginRequiredMixin, TemplateView):
    def get(self, request):
        self.template_name = get_template_dir("add_class", request.is_mobile)
        return render(request, self.template_name)

    def post(self, request):
        if request.user.is_authenticated:
            self.template_name = get_template_dir("add_class", request.is_mobile)
            
            class_name = request.POST.get('name')
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            
            start_date = string_to_date(start_date_str)
            end_date = string_to_date(end_date_str)
            
            if not valid_dates(start_date, end_date):
                error_message = "End date cannot be before start date."
                return render(request, self.template_name, {
                    'error_message': error_message,
                    'name': class_name,
                    'start_date': start_date_str,
                    'end_date': end_date_str,
                })

            Class.objects.create(
                professor_key=request.user,
                class_name=class_name,
                start_date=start_date,
                end_date=end_date,
            )

            return redirect('manage_classes')
        else:
            return redirect('/accounts/login')  # should never reach this, but fall back to redirect   

#TODO: This is unused, where is it intended for?
class ClassDetailsView(View):
    def get(self, request, class_id):
        try:
            working_class = Class.objects.get(id=class_id, professor_key=request.user)
            students = working_class.student_set.all()
            return JsonResponse({
                "class_name": working_class.class_name,
                "is_active": working_class.is_active(),
                "total_students": working_class.total_students(),
                "students": [{"id": s.id, "name": str(s), "score": s.total_score} for s in students],
            })
        except Class.DoesNotExist:
            return JsonResponse({"error": "Class not found or unauthorized"}, status=404)

#Extension of home page when a class is selected.
class ClassHomePageView(LoginRequiredMixin,DetailView):
    model = Class
    context_object_name = "class"
    def get(self, request):
        self.template_name = get_template_dir("class_home", request.is_mobile)

class EditClassView(LoginRequiredMixin, TemplateView):
    def get(self, request, class_id):
        self.template_name = get_template_dir("edit_class", request.is_mobile)
        try:
            selected_class = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            selected_class = None

        return render(request, self.template_name, {
            'class': selected_class,
            'name': selected_class.class_name,
            'start_date': selected_class.start_date.strftime('%Y-%m-%d') if selected_class.start_date else '',
            'end_date': selected_class.end_date.strftime('%Y-%m-%d') if selected_class.end_date else '',
            'is_archived': selected_class.is_archived,
        })

    def post(self, request, class_id):
        self.template_name = get_template_dir("edit_class", request.is_mobile)
        selected_class = Class.objects.get(id=class_id)
        class_name = request.POST.get('name')
        start_date_str = request.POST.get('start_date')
        start_date = string_to_date(start_date_str)
        end_date_str = request.POST.get('end_date')
        end_date = string_to_date(end_date_str)
        is_archived = request.POST.get('is_archived') == 'on'

        if not valid_dates(start_date, end_date):
            error_message = "End date cannot be before start date."
            return render(request, self.template_name, {
                'error_message': error_message,
                'name': class_name,
                'start_date': start_date_str,
                'end_date': end_date_str,
                'is_archived': is_archived,
            })

        selected_class.class_name = class_name
        selected_class.start_date = start_date if start_date else None
        selected_class.end_date = end_date if end_date else None
        selected_class.is_archived = bool(is_archived)
        selected_class.save()
        return redirect('/manageclasses')
    
# Convert date string to date object
def string_to_date(date_string):
    if date_string:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
        
# Ensure that the end date is not before the start date
def valid_dates(start_date, end_date):
    if start_date and end_date and end_date < start_date:
        return False
    return True