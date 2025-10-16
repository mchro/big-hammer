#!/usr/bin/python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
import sys

options = Options()
options.headless = True

#New instantiation
from selenium.webdriver.chrome.service import Service as ChromeService
service = ChromeService(executable_path="/usr/bin/chromedriver")

driver = webdriver.Chrome(options=options, service=service)
try:
    url = 'http://dr.dk/drtv/signin'
    driver.get(url)

    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )

    email_field = driver.find_element(By.ID, "email")
    email_field.send_keys("drlogin2024@gmail.com")
    email_field.send_keys(Keys.RETURN)

    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    sleep(5)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys("Kode1234!")
    password_field.send_keys(Keys.RETURN)

    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "button.profile-circle"))
    )

    button = driver.find_element(By.CSS_SELECTOR, "button.profile-circle")
    button.click()

    for _ in range(20):
        script_get_token = """return localStorage['session.tokens']"""
        result = driver.execute_script(script_get_token)
        if result:
            print(result)
            break

        script_get_local_storage = """return localStorage"""
        result = driver.execute_script(script_get_local_storage)
        print(result, file=sys.stderr)
        sleep(1)

finally:
    driver.quit()

