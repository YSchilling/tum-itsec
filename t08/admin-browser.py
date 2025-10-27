#!/usr/bin/env python3
import os
import sys
import time

# The stdin of this skript is connected to the socket in the contact() method in app.py on our infrastructure

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--headless')

with open('admin-password.txt', 'r') as pw_file:
    password = pw_file.read().strip()

def log(message, *args, **kwargs):
    print(f'\x1b[33m{message}\x1b[0m', *args, **kwargs, file=sys.stderr)


url = sys.stdin.readline().strip()
log(f"Processing request for URL: {url}")
link = sys.stdin.read().strip()

# Step 1 - Establish a session and make sure that we are logged in
try:
    driver = webdriver.Chrome('/usr/bin/chromedriver', options=options)
    wait = WebDriverWait(driver, 1)
    complete = lambda driver: driver.execute_script("return document.readyState") == "complete"

    log('Loading page')
    driver.get(url)
    wait.until(complete)

    user = driver.find_element_by_name("username")
    pw = driver.find_element_by_name("password")
    user.send_keys("admin")
    pw.send_keys(password)

    log('Logging in')
    pw.send_keys(Keys.RETURN)
    wait.until(complete)

    # Step 2 - Click on the link of the user
    log(f'Fetching {link}')
    driver.get(link)
    wait.until(complete)
    time.sleep(2)
    driver.quit()
except:
    import traceback
    traceback.print_exc(file=sys.stderr)
