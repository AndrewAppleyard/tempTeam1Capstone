import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urljoin
from UserClasses import CurrentCourse
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import traceback
import time
from flask import Flask
from cryptography.fernet import Fernet
import os, sys
from flask import Flask, jsonify, request, Blueprint
from sqlalchemy import Column, Integer, String, create_engine, select, text
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
from selenium.common.exceptions import TimeoutException


app = Flask(__name__)


def parseElement(html):
    course = CurrentCourse.CurrentCourse()
    soup = BeautifulSoup(html, 'lxml')
    div = soup.find('div')
    text = div.get_text("_")
    data = text.split("_")

    course.section = data[1]
    course.availability = data[2]
    course.deliveryMode = data[3]
    course.meetingPattern = data[4]
    course.location = data[5]
    course.instructor = data[6]
    course.capacity = data[7]
    course.enrolled = data[8]
    course.academicPeriod = data[9]
    course.startDate = data[10]
    
    return course

def pullCourses():
    print("Starting")
    courses = []
    driver = None
    try:
            service = Service(GeckoDriverManager().install())
            options = Options()
            # options.add_argument("--headless")
            # options.add_argument("--disable-gpu")
            # options.add_argument("--no-sandbox")
            driver = webdriver.Firefox(service=service, options=options)
            driver.get("https://app.powerbi.com/view?r=eyJrIjoiYTMzNmY3ZTgtZDdkNy00M2E2LWFiNGEtNmRlMjhlZjU1ZDliIiwidCI6IjhjMWE4N2NiLTgwYjctNDEzZi05YWU4LTU1YzZhNTM3MDYwNCJ9")
            
            wait = WebDriverWait(driver, 30)
            actions = ActionChains(driver)
            count = 1
            driver.refresh()
            index = 0
            while True:
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".mid-viewport > div:nth-child(1) > div:nth-child("+str(count)+")")))
                if count % 20 == 0:
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    count = 0
                    time.sleep(0.05)
                courses.append(parseElement(element.get_attribute("innerHTML")))
                count = count + 1
                index = index + 1
                print(index)
    except TimeoutException:
        driver.quit()
        return courses
    except Exception as e:
        traceback.print_exc()
    finally:
        if driver is not None:
            driver.quit()

@app.route("/AddCourses", methods=["POST"])
def addCourses():
    courses = []
    role = request.form.get('role')
    if role.casefold() == "admin":
        courses = pullCourses()
    return courses

