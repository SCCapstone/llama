from selenium import webdriver
from selenium.webdriver.common.by import By

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from coldcall.models import *

from ..tests.test_helper import *
from .selenium_helper import *



from selenium.webdriver.support.ui import Select 
from selenium.common.exceptions import NoSuchElementException




class TestRegister(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(2)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_register_valid(self):
        self.driver.get(f"{self.live_server_url}/accounts/register")
        
        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "first_name").send_keys("test")
        self.driver.find_element(By.NAME, "last_name").send_keys("user")
        self.driver.find_element(By.NAME, "email").send_keys("test@gmail.com")
        self.driver.find_element(By.NAME, "password").send_keys("password")

        self.driver.find_element(By.CSS_SELECTOR, "button").click()

        self.assertNotEqual(self.driver.current_url, f"{self.live_server_url}/accounts/register")

    def test_register_invalid(self):
        self.driver.get(f"{self.live_server_url}/accounts/register")
        
        self.driver.find_element(By.NAME, "username").send_keys("####") #invalid characters
        self.driver.find_element(By.NAME, "first_name").send_keys("test")
        self.driver.find_element(By.NAME, "last_name").send_keys("user")
        self.driver.find_element(By.NAME, "email").send_keys("test@gmail.com")
        self.driver.find_element(By.NAME, "password").send_keys("password")

        self.driver.find_element(By.CSS_SELECTOR, "button").click()
        error_text = self.driver.find_element(By.CLASS_NAME, "errorlist").text

        self.assertIn("Enter a valid username", error_text)

class TestLogin(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(2)
        init_prof()

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_valid_login(self):
        self.driver.get(f"{self.live_server_url}/accounts/login")
        
        self.driver.find_element(By.NAME, "username").send_keys(PROF_USERNAME)
        self.driver.find_element(By.NAME, "password").send_keys(PROF_PASSWORD)
        
        self.driver.find_element(By.CSS_SELECTOR, "button").click()

        welcome_text = self.driver.find_element(By.TAG_NAME, "h1").text

        self.assertIn(PROF_USERNAME, welcome_text)

    def test_invalid_login(self):
        self.driver.get(f"{self.live_server_url}/accounts/login")
        
        self.driver.find_element(By.NAME, "username").send_keys(PROF_USERNAME)
        self.driver.find_element(By.NAME, "password").send_keys("thispasswordwillalwaysbewrong")
        
        self.driver.find_element(By.CSS_SELECTOR, "button").click()

        error_text = self.driver.find_element(By.CLASS_NAME, "errorlist").text

        self.assertIn("Please enter a correct username and password.", error_text)

class TestLogout(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(2)
        init_prof()
        automatic_login(self)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_logout(self):
        self.driver.get(f"{self.live_server_url}")

        #ensure actually logged in from automatic_login()
        welcome_text = self.driver.find_element(By.TAG_NAME, "h1").text
        self.assertIn(PROF_USERNAME, welcome_text)

        #logout
        self.driver.find_element(By.XPATH, "//button[contains(., 'Logout')]").click()
        
        #should no longer be at root url, now at login page
        self.assertNotEqual(self.driver.current_url, f"{self.live_server_url}")

#TODO: move to separate file later

class TestHamburgerMenu(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(2)
        init_prof()
        automatic_login(self)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_open_menu(self):
        self.driver.find_element(By.CLASS_NAME, "menuButton").click()

        visibility = self.driver.find_element(By.XPATH, '//*[@id="menu"]').get_attribute("class")

        self.assertIn("show", visibility)

    def test_close_menu(self):
        found_button = self.driver.find_element(By.CLASS_NAME, "menuButton")
        found_button.click()
        found_button.click()

        visibility = self.driver.find_element(By.XPATH, '//*[@id="menu"]').get_attribute("class")

        self.assertNotIn("show", visibility)

class TestCreateClass(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(2)
        init_prof()
        automatic_login(self)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_create_no_date(self):
        self.driver.get(f"{self.live_server_url}/addcourse")
        self.driver.find_element(By.NAME, "name").send_keys(CLASS_NAME)

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        #ensure redirected to root
        self.assertNotEqual(self.driver.current_url, f"{self.live_server_url}")
        
        #find class from selector and ensure it exists
        found_class = self.driver.find_element(By.XPATH, "//*[@id='class_id']/option[2]").text 
        
        self.assertEqual(found_class, CLASS_NAME)

##########################################################################################
class TestDeleteStudent(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(2)
        self.professor = init_prof()
        self.class_obj = init_class(self.professor)
        self.student = Student.objects.create(class_key=self.class_obj, first_name="Test", last_name="Student")
        automatic_login(self)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_delete_student(self):
        self.driver.get(f"{self.live_server_url}/")  # Go to homepage
        
        # Select class from dropdown
        select = Select(self.driver.find_element(By.ID, "class_id"))
        select.select_by_value(str(self.class_obj.id))
        
        # Click the delete button for the student
        delete_button = self.driver.find_element(By.XPATH, f"//a[contains(@href, '/student/{self.student.id}/delete')]")
        delete_button.click()

        # Confirm deletion
        self.driver.switch_to.alert.accept()

        # Ensure student is no longer listed
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.XPATH, f"//td[contains(text(), '{self.student.first_name}')]")

class TestAddStudent(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(2)
        self.professor = init_prof()
        self.class_obj = init_class(self.professor)
        automatic_login(self)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_add_student_manual(self):
        self.driver.get(f"{self.live_server_url}/addeditstudents/manual")

        # Fill out student form
        self.driver.find_element(By.NAME, "first_name").send_keys("John")
        self.driver.find_element(By.NAME, "last_name").send_keys("Doe")
        self.driver.find_element(By.NAME, "usc_id").send_keys("123456789")
        
        # Select class from dropdown
        select = Select(self.driver.find_element(By.NAME, "class_key"))
        select.select_by_value(str(self.class_obj.id))

        # Submit form
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # Redirect to home, check if student is in table
        self.driver.get(f"{self.live_server_url}/")
        student_name = self.driver.find_element(By.XPATH, "//td[contains(text(), 'John')]").text
        self.assertEqual(student_name, "John")

import os

class TestImportStudents(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(3)
        self.professor = init_prof()
        self.class_obj = init_class(self.professor)
        automatic_login(self)

        # Create a temporary CSV file
        self.csv_file = os.path.join(os.getcwd(), "students.csv")
        with open(self.csv_file, "w") as file:
            file.write("usc_id,first_name,last_name,seating\n")
            file.write("987654321,Jane,Doe,FR\n")

    def tearDown(self):
        if self.driver:
            self.driver.quit()
        os.remove(self.csv_file)  # Cleanup CSV file

    def test_import_students(self):
        self.driver.get(f"{self.live_server_url}/addstudents/import")

        # Select class from dropdown
        select = Select(self.driver.find_element(By.NAME, "class_id"))
        select.select_by_value(str(self.class_obj.id))

        # Upload file and submit
        file_input = self.driver.find_element(By.NAME, "file")
        file_input.send_keys(self.csv_file)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # Ensure student appears in table
        self.driver.get(f"{self.live_server_url}/")
        student_name = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Jane')]").text
        self.assertEqual(student_name, "Jane")

class TestViewStudentMetrics(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(2)
        self.professor = init_prof()
        self.class_obj = init_class(self.professor)
        self.student = Student.objects.create(class_key=self.class_obj, first_name="Sam", last_name="Smith")
        automatic_login(self)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_view_student_metrics(self):
        self.driver.get(f"{self.live_server_url}/student/{self.student.id}")

        # Ensure student name appears
        student_name = self.driver.find_element(By.TAG_NAME, "h1").text
        self.assertIn("Sam Smith", student_name)

class TestEditStudentRating(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(2)
        self.professor = init_prof()
        self.class_obj = init_class(self.professor)
        self.student = Student.objects.create(class_key=self.class_obj, first_name="Lisa", last_name="Brown")
        self.rating = StudentRating.objects.create(student_key=self.student, score=3)
        automatic_login(self)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_edit_student_rating(self):
        self.driver.get(f"{self.live_server_url}/student/{self.student.id}/{self.rating.id}")

        # Change rating to 5
        rating_input = self.driver.find_element(By.NAME, "rating")
        rating_input.clear()
        rating_input.send_keys("5")

        # Submit form
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # Ensure updated rating is displayed
        self.driver.get(f"{self.live_server_url}/student/{self.student.id}")
        updated_rating = self.driver.find_element(By.XPATH, "//td[contains(text(), '5')]").text
        self.assertIn("5", updated_rating)  # Allow variations like "5 (5.0 ⭐ average)"