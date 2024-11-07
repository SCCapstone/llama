from django.contrib import admin
from .models import Class, Seating, Student, StudentRating
# Register your models here.
@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'professor_key')
    search_fields = ('class_name',)
    list_filter = ('professor_key',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'class_key', 'seating', 'total_calls', 'absent_calls', 'total_score')
    search_fields = ('first_name', 'last_name')
    list_filter = ('class_key', 'seating')
    ordering = ('last_name',)

@admin.register(StudentRating)
class StudentRatingAdmin(admin.ModelAdmin):
    list_display = ('student_key', 'date', 'attendance', 'prepared', 'score')
    search_fields = ('student_key__first_name', 'student_key__last_name')
    list_filter = ('attendance', 'prepared', 'date')