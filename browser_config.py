from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains  import ActionChains

# import pandas as pd


def create_browser(chromedriver_path, headless=False):
    # Set up Chrome options
    opt = webdriver.ChromeOptions()
    if headless:
        opt.add_argument("--headless")
    opt.add_experimental_option('excludeSwitches', ['enable-logging'])
    opt.add_argument("--disable-popup-blocking")
    opt.add_argument("--disable-extensions")
   

    # Set up logging preferences for performance logs
    d = {
        'goog:loggingPrefs': {'performance': 'ALL'}
    }
    opt.set_capability('goog:loggingPrefs', {'performance': 'ALL'})


    # Set up the Service object for the ChromeDriver executable
    service = Service('driver/chromedriver.exe')

    # Initialize the WebDriver with the service object and options
    browser = webdriver.Chrome(service=service, options=opt)
    browser.implicitly_wait(5)
    
    return browser

