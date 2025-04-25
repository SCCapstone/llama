from django.test import TestCase
from django.contrib.auth.models import User
from coldcall.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import csv
import io
import time
from django.contrib.messages import get_messages

from .test_helper import *
# tests related to the student model and its methods
class TestEmptyStudent(TestCase):
    def setUp(self):
        Student.objects.create(class_key = init_class(init_prof()), first_name = "John", last_name = "Doe")
    # ensure no errors occur when calculating attendance with no saved data
    def test_empty_attendance(self):
        s = Student.objects.get(first_name="John")
        self.assertEqual(0, s.calculate_attendance_rate())
    # ensure no divide by zero error occurs with no data
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
        self.assertEqual(66.67, s.calculate_attendance_rate())
        self.assertEqual("Needs Improvement", s.performance_summary())

class TestStudentImportExport(TestCase):
    def setUp(self):
        self.professor = init_prof()
        self.class_obj = init_class(self.professor)
        # Login the test client since the view requires authentication
        self.client.force_login(self.professor)
        
        # Create some students for export testing
        self.student1 = Student.objects.create(
            class_key=self.class_obj,
            first_name="John",
            last_name="Doe",
            usc_id="1234567",
            email="john@example.com"
        )
        self.student2 = Student.objects.create(
            class_key=self.class_obj,
            first_name="Jane",
            last_name="Smith",
            usc_id="7654321",
            email="jane@example.com"
        )

    def test_import_csv_valid_data(self):
        """Test importing valid student data from CSV"""
        # Use full headers matching what the view expects
        csv_content = "usc_id,email,first_name,last_name\n1122334,alex@example.com,Alex,Johnson\n2233445,sam@example.com,Samantha,Lee"
        csv_file = SimpleUploadedFile("students.csv", csv_content.encode('utf-8'), content_type="text/csv")
        
        # Use the URL pattern with class_id in the path
        url = reverse('add_student_import_with_id', args=[self.class_obj.id])
        response = self.client.post(url, {
            'class_id': self.class_obj.id,
            'students': csv_file
        }, follow=True)
        
        # Allow time for database operations to complete
        time.sleep(0.5)
        
        # Verify students were imported to the database
        self.assertTrue(Student.objects.filter(usc_id="1122334").exists())
        self.assertTrue(Student.objects.filter(usc_id="2233445").exists())

    def test_import_csv_invalid_data(self):
        """Test importing invalid student data from CSV"""
        # Missing required fields
        csv_content = "first_name,last_name\nAlex,Johnson\nSamantha,Lee"
        csv_file = SimpleUploadedFile("students.csv", csv_content.encode('utf-8'), content_type="text/csv")
        
        # Count students before import
        initial_count = Student.objects.count()
        
        # Use the URL pattern with class_id in the path
        url = reverse('add_student_import_with_id', args=[self.class_obj.id])
        response = self.client.post(url, {
            'class_id': self.class_obj.id,
            'students': csv_file
        }, follow=True)
        
        # Check that the response was successful
        self.assertEqual(response.status_code, 200)
        
        # Verify no new students were added (since data is invalid)
        self.assertEqual(Student.objects.count(), initial_count)
        
        # Check for warning message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("No students were imported" in str(message) for message in messages))

    def test_import_csv_duplicate_usc_id(self):
        """Test handling duplicate USC IDs during import"""
        # Create a student first
        original = Student.objects.create(
            class_key=self.class_obj,
            first_name="Original",
            last_name="Student",
            usc_id="5555555",
            email="original@example.com"
        )
        
        # Try to import a student with the same USC ID but different name
        csv_content = "usc_id,email,first_name,last_name\n5555555,dup@example.com,Duplicate,Student"
        csv_file = SimpleUploadedFile("students.csv", csv_content.encode('utf-8'), content_type="text/csv")
        
        # Count students before import
        initial_count = Student.objects.count()
        
        url = reverse('add_student_import_with_id', args=[self.class_obj.id])
        response = self.client.post(url, {
            'class_id': self.class_obj.id,
            'students': csv_file
        }, follow=True)
        
        # Since update_or_create is being used, the count should remain the same
        self.assertEqual(Student.objects.count(), initial_count)
        
        # The existing student should have been updated, not duplicated
        updated_student = Student.objects.get(usc_id="5555555")
        self.assertEqual(updated_student.first_name, "Duplicate")  # Updated name
        self.assertEqual(updated_student.email, "dup@example.com")  # Updated email