from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

from datetime import datetime

from .view_helper import get_template_dir, STUDENT_ATTRIBUTES, RATING_ATTRIBUTES
from ..models import Class, Student, StudentRating

import csv
import io
from zipfile import ZipFile

from openpyxl import Workbook

#Adds a list of students to a given class using a user provided .csv file
class AddStudentImportView(LoginRequiredMixin, TemplateView):

    def get(self, request, class_id=None): 
        self.template_name = get_template_dir("add_student_import", request.is_mobile)
        if class_id: 
            selected_class = Class.objects.get(id=class_id)
        else: 
            selected_class = None
        classes = Class.objects.filter(professor_key = request.user, is_archived=False)
        return render(request, self.template_name, {'classes': classes, 'selected_class': selected_class})
    
    def post(self, request, class_id=None): 
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
            input_class = row.get('class_id', '0').strip()

            input_class = int(input_class) if input_class.isdigit() else 0
            input_class = Class.objects.get(pk=input_class) if input_class else None
            
            #if user has access to provided class in input file, prioritize that first
            #if not, use currently selected class 
            #(this allows for the same student to appear across multiple classes)
            if (input_class is not None and request.user == input_class.professor_key):
                selected_class = input_class
            

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

        return redirect('/')

class ExportClassFileView(View):
    def get(self, request, class_id=None):
        self.template_name = get_template_dir("export_class_file", request.is_mobile)
        classes = Class.objects.filter(professor_key=request.user)
        return render(request, self.template_name, {'classes': classes, 'class_id': class_id})
    
    def post(self, request, class_id=None):
        class_ids = request.POST.getlist('class_id')
        export_type = request.POST.get('export_type')
        file_format = request.POST.get('file_format', 'csv')

        if not class_ids or not export_type:
            return HttpResponseBadRequest("No class ID provided.")
        
        try:
            content_types = {
                'csv': 'text/csv',
                'txt': 'text/plain',
                'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
            extensions = {'csv': '.csv', 'txt': '.txt', 'excel': '.xlsx'}
            content_type = content_types.get(file_format, 'text/csv')
            extension = extensions.get(file_format, '.csv')
        
            # Generates the rows for the given class
            # Simple only exports a list of student attributes, otherwise export student ratings
            def generate_file(class_obj):
                rows = [STUDENT_ATTRIBUTES] if export_type == "simple" else [RATING_ATTRIBUTES]
                for student in class_obj.student_set.all():
                    if export_type == "simple":
                        rows.append(student.get_data_list())
                    else:
                        for rating in student.studentrating_set.all():
                            rows.append([student.usc_id, 
                                         rating.date.replace(tzinfo=None) if isinstance(rating.date, datetime) and rating.date is not None else rating.date, 
                                         rating.attendance, rating.prepared, rating.score, student.class_key.pk])

                return rows
        
            
            response = HttpResponse(content_type=content_type)
            #export a single file, not to zip
            if len(class_ids) == 1:
                class_obj = Class.objects.get(id=class_ids[0], professor_key=request.user)
                filename = f"{class_obj.class_name}_{datetime.now().strftime('%Y%m%d')}{extension}"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'

                rows = generate_file(class_obj)
                # CSV/txt and Excel require different writers
                if file_format in ['csv', 'txt']:
                    writer = csv.writer(response)
                    writer.writerows(rows)
                else:
                    wb = Workbook() 
                    ws = wb.active
                    for row in rows:
                        ws.append(row)
                    wb.save(response)

                return response
            #iterate through each class id, create file, and add to .zip
            zip_buffer = io.BytesIO()
            with ZipFile(zip_buffer, 'w') as zip_file:
                for class_id in class_ids:
                    class_obj = Class.objects.get(id=class_id, professor_key=request.user)

                    rows = generate_file(class_obj)

                    if file_format in ['csv', 'txt']:
                        output = io.StringIO()
                        writer = csv.writer(output)
                        writer.writerows(rows)
                        content = output.getvalue()
                    else: #Excel
                        output = io.BytesIO()
                        wb = Workbook()
                        ws = wb.active
                        for row in rows: 
                            ws.append(row)
                        wb.save(output)
                        content = output.getvalue()

                    timestamp = datetime.now().strftime('%Y%m%d')
                    filename = f"{class_obj.class_name}_{timestamp}{extension}"
                    zip_file.writestr(filename, content)

            response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="class_exports.zip"'
            
            return response
        except Exception as e:
            return HttpResponseBadRequest(f"Error: {str(e)}")

# TODO: Test above to ensure it functions the same, then remove commented section
# Gives the user a .csv file containing information about each student in a class
# class ExportClassFileView2(View):
#     def get(self, request):
#         self.template_name = get_template_dir("export_class_file", request.is_mobile)
#         classes = Class.objects.filter(professor_key=request.user)
#         return render(request, self.template_name, {'classes': classes})
    
#     def post(self, request):
#         class_ids = request.POST.getlist('class_id')
#         export_type = request.POST.get('export_type')
#         file_format = request.POST.get('file_format', 'csv')
        
#         if not class_ids or not export_type:
#             return HttpResponseBadRequest("No class ID provided.")

#         try:
#             # Set content type and extension based on format
#             content_types = {
#                 'csv': 'text/csv',
#                 'txt': 'text/plain',
#                 'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             }
#             extensions = {'csv': '.csv', 'txt': '.txt', 'excel': '.xlsx'}
#             content_type = content_types.get(file_format, 'text/csv')
#             extension = extensions.get(file_format, '.csv')

#             # If only one class is selected, return a single file
#             if len(class_ids) == 1:
#                 class_obj = Class.objects.get(id=class_ids[0], professor_key=request.user)
#                 timestamp = datetime.now().strftime('%Y%m%d')
#                 filename = f"{class_obj.class_name}_{timestamp}{extension}"

#                 if file_format in ['csv', 'txt']:
#                     response = HttpResponse(content_type=content_type)
#                     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#                     writer = csv.writer(response)
                    
#                     if export_type == "simple":
#                         writer.writerow(['usc_id', 'email', 'first_name', 'last_name', 'seating', 'total_calls', 'absent_calls', 'total_score', 'class_id'])
#                         for student in class_obj.student_set.all():
#                             writer.writerow([student.usc_id, student.email, student.first_name, student.last_name,
#                                           student.seating, student.total_calls, student.absent_calls, student.total_score, student.class_key.pk])
#                     else:  # export_type == "all"
#                         writer.writerow(['usc_id', 'date', 'attendance', 'prepared', 'score', 'class_id'])
#                         for student in class_obj.student_set.all():
#                             ratings = StudentRating.objects.filter(student_key=student)
#                             for rating in ratings:
#                                 writer.writerow([student.usc_id, rating.date, rating.attendance,
#                                                rating.prepared, rating.score, student.class_key.pk])
#                 else:  # Excel format
#                     wb = Workbook()
#                     ws = wb.active
                    
#                     if export_type == "simple":
#                         ws.append(['usc_id', 'email', 'first_name', 'last_name', 'seating', 'total_calls', 'absent_calls', 'total_score', 'class_id'])
#                         for student in class_obj.student_set.all():
#                             ws.append([student.usc_id, student.email, student.first_name, student.last_name,
#                                      student.seating, student.total_calls, student.absent_calls, student.total_score, student.class_key.pk])
#                     else:  # export_type == "all"
#                         ws.append(['usc_id', 'date', 'attendance', 'prepared', 'score', 'class_id'])
#                         for student in class_obj.student_set.all():
#                             ratings = StudentRating.objects.filter(student_key=student)
#                             for rating in ratings:
#                                 ws.append([student.usc_id, rating.date, rating.attendance,
#                                          rating.prepared, rating.score, student.class_key.pk])
                    
#                     response = HttpResponse(content_type=content_type)
#                     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#                     wb.save(response)

#                 return response

#             # Multiple classes selected - create ZIP file
#             else:
#                 zip_buffer = io.BytesIO()
#                 with ZipFile(zip_buffer, 'w') as zip_file:
#                     for class_id in class_ids:
#                         class_obj = Class.objects.get(id=class_id, professor_key=request.user)
                        
#                         if file_format in ['csv', 'txt']:
#                             output = io.StringIO()
#                             writer = csv.writer(output)
                            
#                             if export_type == "simple":
#                                 writer.writerow(['usc_id', 'email', 'first_name', 'last_name', 'seating', 'total_calls', 'absent_calls', 'total_score', 'class_id'])
#                                 for student in class_obj.student_set.all():
#                                     writer.writerow([student.usc_id, student.email, student.first_name, student.last_name,
#                                                   student.seating, student.total_calls, student.absent_calls, student.total_score, student.class_key.pk])
#                             else:  # export_type == "all"
#                                 writer.writerow(['usc_id', 'date', 'attendance', 'prepared', 'score', 'class_id'])
#                                 for student in class_obj.student_set.all():
#                                     ratings = StudentRating.objects.filter(student_key=student)
#                                     for rating in ratings:
#                                         writer.writerow([student.usc_id, rating.date, rating.attendance,
#                                                        rating.prepared, rating.score, student.class_key.pk])
                            
#                             content = output.getvalue()
                            
#                         else:  # Excel format
#                             output = io.BytesIO()
#                             wb = Workbook()
#                             ws = wb.active
                            
#                             if export_type == "simple":
#                                 ws.append(['usc_id', 'email', 'first_name', 'last_name', 'seating', 'total_calls', 'absent_calls', 'total_score', 'class_id'])
#                                 for student in class_obj.student_set.all():
#                                     ws.append([student.usc_id, student.email, student.first_name, student.last_name,
#                                              student.seating, student.total_calls, student.absent_calls, student.total_score, student.class_key.pk])
#                             else:  # export_type == "all"
#                                 ws.append(['usc_id', 'date', 'attendance', 'prepared', 'score', 'class_id'])
#                                 for student in class_obj.student_set.all():
#                                     ratings = StudentRating.objects.filter(student_key=student)
#                                     for rating in ratings:
#                                         ws.append([student.usc_id, rating.date, rating.attendance,
#                                                  rating.prepared, rating.score, student.class_key.pk])
                            
#                             wb.save(output)
#                             content = output.getvalue()

#                         timestamp = datetime.now().strftime('%Y%m%d')
#                         filename = f"{class_obj.class_name}_{timestamp}{extension}"
#                         zip_file.writestr(filename, content)

#                 response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
#                 response['Content-Disposition'] = f'attachment; filename="class_exports.zip"'
                
#                 return response
            
#         except Exception as e:
#             return HttpResponseBadRequest(f"Error: {str(e)}")