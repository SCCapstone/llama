from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

from datetime import datetime

from .view_helper import get_template_dir
from ..models import Class, Student, StudentRating

import csv

import time

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
        student_file = request.FILES.get('students')
        rating_file = request.FILES.get("ratings")
        
        # Check if the file type is csv
        if not student_file.name.endswith('.csv'):
            return HttpResponseBadRequest("Invalid file type. Please select a CSV file.")
        
        try:
            selected_class = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return HttpResponseBadRequest("Invalid class ID.")
        
        decoded_file = student_file.read().decode('utf-8').splitlines()
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

            if not usc_id or not email or not first_name or not last_name:
                continue; # Skip row if field is empty 

            # we want students to be repeated but not within a class. 
            Student.objects.update_or_create(
                usc_id = usc_id,
                defaults={
                    'email': email, 
                    'first_name': first_name, 
                    'last_name': last_name,
                    'class_key': selected_class,
                    'seating': seating if seating in ['FR', "Front Right", 'FM', "Front Middle", 'FL', "Front Left", 'BR', "Back Right", 'BM', "Back Middle", 'BL', "Back Left", 'NA', "None"] else 'NA',
                    'total_calls': int(total_calls) if total_calls.isdigit() else 0,
                    'absent_calls': int(absent_calls) if absent_calls.isdigit() else 0,
                    'total_score': int(total_score) if total_score.isdigit() else 0
                }
            )     

        # handle rating import if file is present    
        start_time = time.time()
        if rating_file:
            decoded_file = rating_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            rows = []
            student_ids = set()        

            for row in reader:
                usc_id = row.get('usc_id', '').strip()
                date = row.get('date', '').strip()
                #ensure valid data is present for key, skip otherwise
                if not usc_id or not date:
                    continue
                rows.append(row)
                student_ids.add(usc_id)
            #bulk grab students using SQL IN search
            students = {
                student.usc_id: student for student in Student.objects.filter(usc_id__in=student_ids)
            }
            #use new set tos tore student references rather than ids
            updated_students = set()
            #combine each query into one all-or-nothing query
            with transaction.atomic():
                for row in rows:
                    usc_id = row.get('usc_id', '').strip()
                    date = row.get('date', '').strip()
                    attendance = row.get('attendance', "TRUE").strip().upper()
                    prepared = row.get('prepared', "FALSE").strip().upper()
                    score = row.get('score', '0').strip()
                    #grab student from existing set
                    student = students.get(usc_id)

                    StudentRating.objects.update_or_create(
                        student_key = student,
                        date = datetime.fromisoformat(date),
                        defaults={
                            'attendance': attendance == "TRUE",
                            'prepared': prepared == "TRUE",
                            'score': int(score) if score.isdigit() else 0
                        }
                    )

                    updated_students.add(student)

            with transaction.atomic():
                for student in updated_students:
                    student.recalculate_all()
        end_time = time.time()
        print(f"{end_time - start_time} s")

        return redirect('/')

# Gives the user a .csv file containing information about each student in a class
class ExportClassFileView(View): 
    def get(self, request): 
        self.template_name = get_template_dir("export_class_file", request.is_mobile)
        classes = Class.objects.filter(professor_key=request.user)
        return render(request, self.template_name, {'classes': classes})
    
    def post(self, request):
        class_id = request.POST.get('class_id')
        export_type = request.POST.get('export_type')
        if class_id and export_type: 
            if export_type == "simple": #just students
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
            elif export_type == "all": #every student metric with primary key attached
                try: 
                    class_to_export = Class.objects.get(id=class_id, professor_key=request.user)
                    students = class_to_export.student_set.all()
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = f'attachment; filename="{class_to_export.class_name}_ratings.csv"'
                    writer = csv.writer(response)
                    writer.writerow(['usc_id', 'date', 'attendance', 'prepared', 'score'])
                    for student in students:
                        ratings = StudentRating.objects.filter(student_key = student)
                        for rating in ratings:
                            writer.writerow([student.usc_id, rating.date, rating.attendance, rating.prepared, rating.score])
                    return response
                except Class.DoesNotExist:
                    return HttpResponseBadRequest("Invalid class ID.")
                
        else: 
            return HttpResponseBadRequest("No class ID provided.")