from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

from .view_helper import get_template_dir
from ..models import Class, Student

import csv

#Adds a list of students to a given course using a user provided .csv file
class AddStudentImportView(LoginRequiredMixin, TemplateView):

    def get(self, request): 
        self.template_name = get_template_dir("add_student_import", request.is_mobile)
        class_id = request.GET.get('class_id')
        if class_id: 
            selected_class = Class.objects.get(id=class_id)
        else: 
            selected_class = None
        classes = Class.objects.filter(professor_key = request.user)
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
            email = row.get('email', '').strip()
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
                email = email, 
                first_name = first_name, 
                last_name = last_name, 
                class_key = selected_class, 
                seating = seating if seating in ['FR', "Front Right", 'FM', "Front Middle", 'FL', "Front Left", 'BR', "Back Right", 'BM', "Back Middle", 'BL', "Back Left", 'NA', "None"] else 'NA',
                total_calls = int(total_calls) if total_calls.isdigit() else 0, 
                absent_calls = int(absent_calls) if absent_calls.isdigit() else 0, 
                total_score = int(total_score) if total_score.isdigit() else 0 
            )                     

        return redirect('/')

# Gives the user a .csv file containing information about ech student in a class
class ExportClassFileView(View): 
    def get(self, request): 
        self.template_name = get_template_dir("export_class_file", request.is_mobile)
        classes = Class.objects.filter(professor_key=request.user)
        return render(request, self.template_name, {'classes': classes})
    
    def post(self, request):
        class_id = request.POST.get('class_id')
        if class_id: 
            try: 
                class_to_export = Class.objects.get(id=class_id, professor_key=request.user)
                students = class_to_export.student_set.all()
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{class_to_export.class_name}.csv"'
                writer = csv.writer(response)
                writer.writerow(['usc_id', 'email', 'first_name', 'last_name', 'seating', 'total_calls', 'absent_calls', 'total_score'])
                for student in students:
                    writer.writerow([student.usc_id, student.email, student.first_name, student.last_name, student.seating, student.total_calls, student.absent_calls, student.total_score])
                return response
            except Class.DoesNotExist:
                return HttpResponseBadRequest("Invalid class ID.")
        else: 
            return HttpResponseBadRequest("No class ID provided.")