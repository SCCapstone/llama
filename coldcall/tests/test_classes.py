from django.test import TestCase
from django.contrib.auth.models import User
from coldcall.models import *

# Create your tests here.
class TestEmptyClass(TestCase):
    def setUp(self):
        professor = User.objects.create_user(username="test", password="password", first_name = "John", last_name = "Doe", email="test@example.com")
        Class.objects.create(professor_key = professor, class_name = "Test101")

    def test_empty_active(self):
        class_obj = Class.objects.get(class_name = "Test101")
        self.assertTrue(class_obj.is_active())

    def test_empty_student_count(self):
        class_obj = Class.objects.get(class_name = "Test101")
        self.assertEqual(0, class_obj.total_students())

    def test_empty_student_performance(self):
        class_obj = Class.objects.get(class_name = "Test101")
        self.assertEqual([], class_obj.get_student_performance())

