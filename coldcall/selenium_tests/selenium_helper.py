#Helper file containing commonly used setup cases for various tests
from selenium.webdriver.common.by import By

from ..tests.test_helper import *


def automatic_login(s):
        s.driver.get(f"{s.live_server_url}/accounts/login")
        
        s.driver.find_element(By.NAME, "username").send_keys(PROF_USERNAME)
        s.driver.find_element(By.NAME, "password").send_keys(PROF_PASSWORD)
        
        s.driver.find_element(By.CSS_SELECTOR, "button").click()