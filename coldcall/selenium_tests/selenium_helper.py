#Helper file containing commonly used setup cases for various tests
from selenium.webdriver.common.by import By

from ..tests.test_helper import *

# automatically login using exising sample user for pages requiring login
def automatic_login(s):
        s.driver.get(f"{s.live_server_url}/accounts/login")
        
        s.driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(PROF_USERNAME)
        s.driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(PROF_PASSWORD)
        
        s.driver.find_element(By.CSS_SELECTOR, "button").click()