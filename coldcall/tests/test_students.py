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

    # make sure that the student is created with a valid usc_id
    def test_student_creation_invalid_usc_id(self):
        with self.assertRaises(Exception):
            Student.objects.create(
                class_key=init_class(init_prof()),
                first_name="Jane",
                last_name="Doe",
                usc_id="INVALID",
                seating="FR"
            )

    # make sure attendance rate is zero when there are no calls
    def test_attendance_rate_zero_calls(self):
        s = Student.objects.get(first_name="John")
        self.assertEqual(0, s.calculate_attendance_rate())

    # add multiple scores and make sure the average is correct
    def test_average_score_multiple_scores(self):
        s = Student.objects.get(first_name="John")
        StudentRating.objects.create(student_key=s, score=3)
        StudentRating.objects.create(student_key=s, score=5)
        s.recalculate_all()
        self.assertEqual(4.0, s.get_average_score())

    # make sure different attendance rates return the correct performance summary
    def test_performance_summary_various_attendance(self):
        s = Student.objects.get(first_name="John")

        # student should already be excellent rating
        StudentRating.objects.create(student_key=s, attendance=True)
        s.recalculate_all()
        self.assertEqual("Excellent", s.performance_summary())

        # .8 attendance rate should equal 'good'
        s.absent_calls = 1
        s.total_calls = 5
        s.save()
        self.assertEqual("Good", s.performance_summary())

        # .25 attendance rate should equal 'needs improvement'
        s.absent_calls = 3
        s.total_calls = 4
        s.save()
        self.assertEqual("Needs Improvement", s.performance_summary())

    # make a new rating and make sure the student is updated
    def test_recalculate_methods(self):
        s = Student.objects.get(first_name="John")
        StudentRating.objects.create(student_key=s, score=4, attendance=True)
        s.recalculate_all()
        self.assertEqual(1, s.total_calls)
        self.assertEqual(0, s.absent_calls)
        self.assertEqual(4, s.total_score)

    # make sure the average score is zero when there are no present calls
    def test_average_score_no_present_calls(self):
        s = Student.objects.get(first_name="John")
        s.total_calls = 2
        s.absent_calls = 2
        s.total_score = 0
        s.save()
        self.assertEqual(0, s.get_average_score())

    # make sure the performance summary is 'needs improvement' when there are no ratings
    def test_performance_summary_no_ratings(self):
        s = Student.objects.get(first_name="John")
        s.total_calls = 0
        s.absent_calls = 0
        s.save()
        self.assertEqual("Needs Improvement", s.performance_summary())

    # add multiple student ratings and make sure the student is updated
    def test_multiple_student_ratings(self):
        s = Student.objects.get(first_name="John")
        StudentRating.objects.create(student_key=s, score=5, attendance=True)
        StudentRating.objects.create(student_key=s, score=3, attendance=True)
        StudentRating.objects.create(student_key=s, score=4, attendance=False)
        s.recalculate_all()
        self.assertEqual(3, s.total_calls)
        self.assertEqual(1, s.absent_calls)
        self.assertEqual(8, s.total_score)
        self.assertEqual(66.66666666666666, s.calculate_attendance_rate())
        self.assertEqual("Needs Improvement", s.performance_summary())