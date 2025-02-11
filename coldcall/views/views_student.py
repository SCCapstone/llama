from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, TemplateView
from django.urls import reverse

from .view_helper import get_template_dir
from ..models import Class, Student, StudentRating

import json

#Allows the user to add a new student to a class.
class AddEditStudentManualView(LoginRequiredMixin,TemplateView):
     # added this to help get classes for the add new student manual page
    def get(self, request, student_id=None):
        self.template_name = get_template_dir("addedit_student_manual", request.is_mobile)
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

#Providdes a read-only table of a student's data.
class StudentMetricsView(LoginRequiredMixin,DetailView):
    model = Student
    context_object_name = "student"

    def get_context_data(self, **kwargs): # kwargs variable allowing us to accept any additional keyword arguemnts
        self.template_name = get_template_dir("student_metrics", self.request.is_mobile)
        
        context = super().get_context_data(**kwargs)
        student = Student(self.object)
        attendance_rate = student.calculate_attendance_rate()
        performance = student.performance_summary()
        context['attendance_difference'] = student.total_calls - student.absent_calls
        context['attendance_rate'] = attendance_rate
        context['performance_summary'] = performance
        context['student_perf'] = StudentRating.objects.filter(student_key = student.pk)
        
        ratings = StudentRating.objects.filter(student_key = student.pk).order_by('date').values('date', 'score', 'attendance', 'prepared')
        # convert ratings into json parsable object, date isn't serializable[?]
        ratings_list = list(ratings)
        # for rating in ratings_list:
        #     rating['date'] = rating['date'].strftime("%Y-%m-%d")
        
        # context['rating_list'] = json.dumps(ratings_list)
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
        

class StudentDeleteView(View):
    def post(self, request, student_id):
        try: 
            student = get_object_or_404(Student, id=student_id)
            student.delete()
        
            return redirect('home')
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)