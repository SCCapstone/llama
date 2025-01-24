from selenium import webdriver
from selenium.webdriver.common.by import By

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase

class TestRegister(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

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

        self.assertTrue(error_text.__contains__("Enter a valid username."))