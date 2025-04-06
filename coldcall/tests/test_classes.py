from django.test import TestCase
from django.contrib.auth.models import User
from coldcall.models import *

from .test_helper import *
# Tests related to the class model
class TestEmptyClass(TestCase):
    def setUp(self):
        professor = init_prof()
        init_class(professor)
    # should always be active by default
    def test_empty_active(self):
        class_obj = Class.objects.get(class_name = "Test101")
        self.assertTrue(class_obj.is_active())

    def test_empty_student_count(self):
        class_obj = Class.objects.get(class_name = "Test101")
        self.assertEqual(0, class_obj.total_students())
    # check that no errors are thrown when getting student performance
    def test_empty_student_performance(self):
        class_obj = Class.objects.get(class_name = "Test101")
        self.assertEqual([], class_obj.get_student_performance())

class TestClassWithEmptyStudents(TestCase):
    def setUp(self):
        professor = init_prof()
        class_obj = init_class(professor)
        for i in range(1,6):
            Student.objects.create(class_key = class_obj, first_name = i, last_name = i+10) #create 5 blank students
    
    def test_total_students(self):
        class_obj = Class.objects.get(class_name = "Test101")
        self.assertEqual(class_obj.total_students(), 5)

    def test_student_performance(self):
        class_obj = Class.objects.get(class_name = "Test101")
        performance = class_obj.get_student_performance()
        for i in performance:
            if i["score"] != 0 or i["attendance_rate"] != 0:
                self.assertEqual(i, False) #show invalid option and break out of for loop if invalid
        self.assertTrue(True) #always return true if prior loop succeeds

class TestClassWithValidStudents(TestCase):
    def setUp(self):
        professor = init_prof()
        class_obj = init_class(professor)
        for i in range(1,6):
            s = Student.objects.create(class_key = class_obj, first_name = i, last_name = i+10)
            StudentRating.objects.create(student_key = s, score=3)
            s = s.recalculate_all()
    
    def test_student_performance(self):
        class_obj = Class.objects.get(class_name = "Test101")
        performance = class_obj.get_student_performance()
        for i in performance:
            if i["score"] != 3 or i["attendance_rate"] != 100:
                self.assertEqual(i, False)
        self.assertTrue(True)