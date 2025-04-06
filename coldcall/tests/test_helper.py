# helper functions for setting up tests
from django.contrib.auth.models import User
from coldcall.models import *

import datetime
import random
from django.utils import timezone
from django.test import TestCase

# Constants to establish tests
PROF_USERNAME = "test"
PROF_PASSWORD = "password"
PROF_NAME = "JOHN"
PROF_LASTNAME = "DOE"
PROF_EMAIL = "test@example.com"

CLASS_NAME = "Test101"
CLASS_PREFIX = "C"

STUDENT_FIRST_PREFIX = "First"
STUDENT_LAST_PREFIX = "Last"

# creates a new user account for a sample professor to populate later
def init_prof():
    prof = User.objects.create_user(username=PROF_USERNAME, password=PROF_PASSWORD, first_name = PROF_NAME, last_name = PROF_LASTNAME, email=PROF_EMAIL)
    UserData.objects.create(user=prof, seen_onboarding=True)
    return prof

#creates an empty class with no additional data
def init_class(prof):
    return Class.objects.create(professor_key = prof, class_name = CLASS_NAME)

#creates a given number of classes with active dates
def init_sample_classes(prof: User, n) -> list[Class]:
    created_classes = []
    for i in range(n):
        new_class = Class.objects.create(professor_key = prof, class_name = CLASS_PREFIX + str(i), start_date = timezone.now(), end_date = timezone.now() + datetime.timedelta(days=10))
        created_classes.append(new_class)
    return created_classes

#creates a given number of students with no data
def init_sample_students(class_obj: Class, class_size) -> list[Student]:
    created_students = []
    for i in range(class_size):
        new_student = Student.objects.create(usc_id = str(i), first_name = STUDENT_FIRST_PREFIX + str(i), last_name = STUDENT_LAST_PREFIX + str(i), class_key = class_obj)
        created_students.append(new_student)
    return created_students

#creates a given number of students with random ratings
def populate_student_random(student: Student, count, absent_count):
    for i in range(count):
        score = random.randint(1,5)
        student.add_rating(is_present=True, is_prepared=True, score=score)
    for i in range(absent_count):
        student.add_rating(is_present=False, is_prepared=False, score=-1)
#creates a given number of students with a provided rating and amount of absences    
def populate_student_constant(student:Student, score, count, absent_count):
    for i in range(count):
        student.add_rating(is_present=True, is_prepared=True, score=score)
    for i in range(absent_count):
        student.add_rating(is_present=False, is_prepared=False, score=-1)

# subtests for testing helper functions
class HelperFunctionsTest(TestCase):
    def setUp(self):
        self.prof = init_prof()

    def test_create_one_class(self):
        init_sample_classes(self.prof, 1)
        self.assertEqual(1, len(Class.objects.filter(professor_key = self.prof)))
        self.assertEqual(CLASS_PREFIX + "0", Class.objects.get(pk=1).class_name)

    def test_create_multiple_classes(self):
        init_sample_classes(self.prof, 5)
        #check all were created, not checking contents
        self.assertEqual(5, len(Class.objects.filter(professor_key = self.prof)))
        #in proper order (using last element)
        self.assertEqual(CLASS_PREFIX + "4", Class.objects.get(pk=5).class_name)
    #creates a new class and checks to see if the student was properly added
    def test_create_sample_student(self):
        new_class = init_sample_classes(self.prof, 1)[0]
        init_sample_students(new_class, 1)

        self.assertEqual(1, len(Student.objects.filter(class_key = new_class)))
        self.assertEqual("0", Student.objects.get(pk=1).usc_id)
    #creates a new class and checks to see if each student was properly added, checking the last student
    def test_create_sample_students(self):
        new_class = init_sample_classes(self.prof, 1)[0]
        init_sample_students(new_class, 5)

        self.assertEqual(5, len(Student.objects.filter(class_key = new_class)))
        self.assertEqual("4", Student.objects.get(pk=5).usc_id)
    # checks to see if average score is properly calculated with consistent values
    def test_populate_student_constant(self):
        new_class = init_sample_classes(self.prof, 1)[0]
        new_student = init_sample_students(new_class, 1)[0]
        populate_student_constant(new_student, 3, 4, 1)

        self.assertEqual(5, new_student.total_calls)
        self.assertEqual(1, new_student.absent_calls)
        self.assertEqual(new_student.get_average_score(), 3.0)
        self.assertEqual(new_student.calculate_attendance_rate(), 80.0)

    def test_populate_student_random(self):
        new_class = init_sample_classes(self.prof, 1)[0]
        new_student = init_sample_students(new_class, 1)[0]
        populate_student_random(new_student, 4, 1)

        self.assertEqual(5, new_student.total_calls)
        self.assertEqual(1, new_student.absent_calls)
        # can't check to a constant value, compare to minimum possible and maximum possible
        self.assertGreaterEqual(new_student.get_average_score(), 1.0)
        self.assertLessEqual(new_student.get_average_score(), 5.0)

        self.assertEqual(new_student.calculate_attendance_rate(), 80.0)
