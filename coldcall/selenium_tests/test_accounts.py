from selenium import webdriver
from selenium.webdriver.common.by import By

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from coldcall.models import *

from ..tests.test_helper import *
from .selenium_helper import *

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

        visibility = self.driver.find_element(By.CLASS_NAME, "menu").get_attribute("style")
        self.assertIn("flex", visibility)

    def test_close_menu(self):
        found_button = self.driver.find_element(By.CLASS_NAME, "menuButton")
        found_button.click()
        found_button.click()

        visibility = self.driver.find_element(By.CLASS_NAME, "menu").get_attribute("style")

        self.assertIn("none", visibility)

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