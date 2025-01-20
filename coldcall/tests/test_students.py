from django.test import TestCase
from django.contrib.auth.models import User
from coldcall.models import *

from .test_helper import *

class TestEmptyStudent(TestCase):
    def setUp(self):
        Student.objects.create(class_key = init_class(init_prof()), first_name = "John", last_name = "Doe")
    
    def test_empty_attendance(self):
        s = Student.objects.get(first_name="John")
        self.assertEqual(0, s.calculate_attendance_rate())

    def test_empty_avg_score(self):
        s = Student.objects.get(first_name="John")
        self.assertEqual(0, s.get_average_score())

    def test_empty_performance(self):
        s = Student.objects.get(first_name="John")
        self.assertEqual("Needs Improvement", s.performance_summary())

    def test_add_good_performance(self):
        s = Student.objects.get(first_name="John")
        StudentRating.objects.create(student_key = s)
        s = s.recalculate_all()
        self.assertEqual("Excellent", s.performance_summary())