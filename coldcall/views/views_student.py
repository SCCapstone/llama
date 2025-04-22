from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, TemplateView
from django.urls import reverse

from .view_helper import get_template_dir
from ..models import Class, Student, StudentRating, StudentNote

import json

class AddStudentManualView(LoginRequiredMixin, TemplateView):
    def get(self, request, class_id=None):
        self.template_name = get_template_dir("addedit_student_manual", request.is_mobile)
        if class_id: 
            selected_class = Class.objects.get(id=class_id)
        else: 
            selected_class = None

        classes = Class.objects.filter(professor_key = request.user, is_archived=False)

        return render(request, self.template_name, {'classes': classes, 'selected_class': selected_class})
    def post(self, request, class_id=None):
        self.template_name = get_template_dir("addedit_student_manual", request.is_mobile)
        usc_id = request.POST.get('usc_id').upper()
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        class_key_id = request.POST.get('class_key')
        seating = request.POST.get('seating')
        email = request.POST.get('email')

        try:
            class_key = Class.objects.get(id=class_key_id)
        except Class.DoesNotExist:
            return HttpResponseBadRequest("Invalid class ID.")
        
        #helper function to ensure input is valid
        def same_length_arr(*arrays):
            lengths = [len(arr) for arr in arrays]
            return all(length == lengths[0] for length in lengths)
        
        # convert all into lists if user provided multiple inputs, remove whitespace
        usc_id = [s.strip() for s in usc_id.split(",")]
        first_name = [s.strip() for s in first_name.split(",")]
        last_name = [s.strip() for s in last_name.split(",")]
        email = [s.strip() for s in email.split(",")]

        if not same_length_arr(usc_id, first_name, last_name, email):
            messages.error(request, "All fields must have the same number of entries.")
            return render(request, self.template_name, {'classes': Class.objects.filter(professor_key=request.user), 'usc_id': array_to_string(usc_id), 'first_name': array_to_string(first_name), 'last_name': array_to_string(last_name), 'email': array_to_string(email), 'seating': seating, 'selected_class': class_key})
        
        # add all students at once, abort on failure
        with transaction.atomic():
            for i in range(len(usc_id)):
                if len(usc_id[i]) > 9:
                    messages.error(request, "USC ID must be 9 characters long.")
                    return render(request, self.template_name, {'classes': Class.objects.filter(professor_key=request.user), 'usc_id': array_to_string(usc_id), 'first_name': array_to_string(first_name), 'last_name': array_to_string(last_name), 'email': array_to_string(email), 'seating': seating, 'selected_class': class_key})
                
                student = Student(
                    usc_id=usc_id[i],
                    first_name=first_name[i],
                    last_name=last_name[i],
                    class_key=class_key,
                    seating=seating,
                    email=email[i]
                )
                student.save()

        if len(usc_id) == 1:
            messages.success(request, f"Student {first_name[0]} {last_name[0]} added successfully!")
        else:
            messages.success(request, f"{len(usc_id)} students added successfully!")

        # Clear the form fields and allow the user to add another student
        return render(request, self.template_name, {'classes': Class.objects.filter(professor_key=request.user), 'selected_class': class_key})

class EditStudentView(LoginRequiredMixin, TemplateView):
    def get(self, request, student_id=None):
        self.template_name = get_template_dir("addedit_student_manual", request.is_mobile)
        classes = Class.objects.filter(professor_key = request.user)
        try:
            student = Student.objects.get(id=student_id)
            selected_class = student.class_key
        except Student.DoesNotExist:
            student = None

        return render(request, self.template_name, {
            'student': student,
            'classes': classes,
            'usc_id': student.usc_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'seating': student.seating,
            'selected_class': selected_class
        })
    def post(self, request, student_id=None):
        self.template_name = get_template_dir("addedit_student_manual", request.is_mobile)
        usc_id = request.POST.get('usc_id').upper()
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        class_key_id = request.POST.get('class_key')
        seating = request.POST.get('seating')
        email = request.POST.get('email')

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
            student.email = email
            if len(usc_id) > 9:
                messages.error(request, "USC ID must be 9 characters long.")
                return render(request, self.template_name, {'classes': Class.objects.filter(professor_key=request.user), 'student': student, 'usc_id': usc_id, 'first_name': first_name, 'last_name': last_name, 'email': email, 'seating': seating, 'selected_class': class_key})
            student.save()
        else:
            return HttpResponseBadRequest("Student ID is required for updating.")

        # send the user back to home page
        return redirect('/')            

#Providdes a read-only table of a student's data.
class StudentMetricsView(LoginRequiredMixin,DetailView):
    model = Student
    context_object_name = "student"

    def get_context_data(self, **kwargs): # kwargs variable allowing us to accept any additional keyword arguemnts
        self.template_name = get_template_dir("student_metrics", self.request.is_mobile)
        
        context = super().get_context_data(**kwargs)
        #self.object returns Student object(Student object(pk))
        #grab pk to fix this
        student = self.object
        attendance_rate = student.calculate_attendance_rate()
        performance = student.performance_summary()
        context['attendance_difference'] = student.total_calls - student.absent_calls
        context['attendance_rate'] = attendance_rate
        context['performance_summary'] = performance
        context['student_perf'] = StudentRating.objects.filter(student_key = student.pk).order_by('date')
        context['notes'] = StudentNote.objects.filter(student_key = student.pk)
        
        ratings_list = list(context['student_perf'].values('date', 'score', 'attendance', 'prepared'))
        # convert ratings into json parsable object, date isn't serializable[?]

        context['rating_list'] = ratings_list
        return context

#TODO: make this and StudentMetricsView restrict access to authorized users only
class StudentRatingEditView(LoginRequiredMixin, View):
    def get(self, request, pk, performance_id):
        self.template_name = get_template_dir("student_rating_edit", request.is_mobile)
        student = Student.objects.get(pk = pk)
        rating = StudentRating.objects.get(pk = performance_id)
        context = {
            'pk': pk,
            'performance_id': performance_id,
            'student': student,
            'rating': rating
        }
        return render(request, self.template_name, context)

    def post(self, request, pk, performance_id):
        student = Student.objects.get(pk=pk)
        rating = StudentRating.objects.get(pk=performance_id)

        print(request.POST)
        attendance = 'present' in request.POST
        prepared = 'prepared' in request.POST
        print(attendance)
        print(prepared)
        try:
            score = int(request.POST.get('rating'))
        except:
            score = 5

        rating.attendance = attendance
        rating.prepared = prepared
        rating.score = score
        rating.save()

        student.recalculate_all()
        return redirect("/student/" + str(pk))   
        
#Allows editing of a student's existing data.     
class StudentUpdateView(View):
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
    
    def transfer_student(request, student_id):
        student = get_object_or_404(Student, id=student_id)
        
        if request.method == "POST":
            new_class_id = request.POST.get("new_class_id")
            new_class = get_object_or_404(Class, id=new_class_id)
            student.class_key = new_class
            student.save()
            return redirect('home')  # Redirect to homepage or student list

        classes = Class.objects.exclude(id=student.class_key.id)  # Exclude current class
        return render(request, "coldcall/transfer_student.html", {"student": student, "classes": classes})

        
#
class StudentDeleteView(View):
    def post(self, request, student_id):
        try: 
            student = get_object_or_404(Student, id=student_id)
            student.delete()
        
            return redirect('home')
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

class StudentDropView(View):
    def post(self, request, student_id):
        try: 
            student = get_object_or_404(Student, id=student_id)
            student.dropped = not student.dropped  # Toggle the dropped status
            student.save()
        
            return redirect('home')
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
class AddNoteView(View):
    def post(self, request, student_id):
        student = get_object_or_404(Student, id=student_id)
        note_content = request.POST.get('note')

        if note_content:
            new_note = StudentNote(student_key=student, note=note_content, class_key=student.class_key)
            new_note.save()
            return redirect('student_metrics', pk=student_id)
        

class DeleteNoteView(View):
    def post(self, request, student_id, note_id):
            note = get_object_or_404(StudentNote, pk=note_id)
            
            if note.student_key.class_key.professor_key != request.user:
                return HttpResponseForbidden("You are not allowed to delete this note.")
            
            # Delete the note
            note.delete()
            
            # Redirect back to the student's notes page
            return redirect('student_metrics', pk=student_id)
    
def array_to_string(array):
    return ', '.join(array) if isinstance(array, list) else array