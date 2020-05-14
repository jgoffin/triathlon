import csv
import os
from datetime import date
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

BASE_DIR = '/users/jacobgoffin/Documents/Github/triathlon'


class Complaint:

    def __init__(self, data={}):

        self.data = data


class Writer:
    def __init__(self,
                 name='default'
                 ):
        self.name = name
        self.filepath = os.path.join(BASE_DIR, f'data/{self.name}_{date.today()}.csv')
        self.file = open(self.filepath, 'w')
        self.headers = ['age', 'gender', 'swim_time', 'run_time', 'bike_time', 't1', 't2']
        self.writer = csv.DictWriter(f=self.file, fieldnames=self.headers)
        self.writer.writeheader()



def grab_text(driver, path, wait_time=5):
    try:
        text = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, path))).text
        print(f"Found: {text}")
        return text
    except Exception as e:
        print("Can't find " + path)
        print(f"Exception: {e}")
        return None


def grab_attribute(driver, path, attribute, wait_time=5):
    try:
        text = (WebDriverWait(driver, wait_time)
                .until(EC.presence_of_element_located((By.XPATH, path)))
                .get_attribute(attribute)
                )
        print(f"Found: {text}")
        return text
    except Exception as e:
        print("Can't find " + path)
        print(f"Exception: {e}")
        return None


def grab_element(driver, path, wait_time=5):
    try:
        return WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, path)))
    except Exception as e:
        print("Can't find " + path)
        print(f"Exception: {e}")
        return None


def grab_child_attribute(web_element, path, attribute, wait_time=5):
    try:
        text = web_element.find_element_by_xpath(f".//{path}").get_attribute(attribute)
        print(f"Found: {text}")
        return text
    except Exception as e:
        print(f"Can't find path: {path} with attribute{attribute}")
        print(f"Exception: {e}")
        return None


def grab_child_text(web_element, path, wait_time=5):
    try:
        text = web_element.find_element_by_xpath(f".//{path}").text
        print(f"Found: {text}")
        return text
    except Exception as e:
        print("Can't find " + path)
        print(f"Exception: {e}")
        return None
