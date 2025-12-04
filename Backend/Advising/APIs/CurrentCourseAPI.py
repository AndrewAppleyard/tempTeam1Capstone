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
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from functools import wraps
from Advising.APIs import URL

bp = Blueprint('CurrentCourseAPI', __name__, url_prefix='/CurrentCourses')

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

path = os.path.abspath(__file__)
directory = os.path.dirname(path)
databaseURL = URL.decrypt(directory + "/config/config.txt", directory + "/config/.gitignore.key")
engine = create_engine(databaseURL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def role_required(*required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            token = get_jwt()
            if token.get("Role") not in required_roles:
                return jsonify({"message": "Access denied!"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def parseElement(html):

    courses = []

    with Session(engine) as session:
        try:
            soup = BeautifulSoup(html, 'lxml')
            div = soup.find('div')
            text = div.get_text("_")
            data = text.split("_")

            existing = session.query(CurrentCourse.CurrentCourseMap).filter(CurrentCourse.CurrentCourseMap.section == data[1]).first()

            if existing:
                existing.courseavailability = data[2]
                existing.deliverymode = data[3]
                existing.meetingpattern = data[4]
                existing.courselocation = data[5]
                existing.instructor = data[6]
                existing.capacity = data[7]
                existing.enrolled = data[8]
                existing.academicperiod = data[9]
                existing.startdate = data[10]
            else:
                newCourse = CurrentCourse.CurrentCourseMap(
                    section=data[1],           
                    courseavailability=data[2],
                    deliverymode=data[3],
                    meetingpattern=data[4],
                    courselocation=data[5],
                    instructor=data[6],
                    capacity=data[7],
                    enrolled=data[8],
                    academicperiod=data[9],
                    startdate=data[10],
                )
                session.add(newCourse)
            
            courses.append(data[1])
        except Exception as e:
            print(f"Failed Insert: {newCourse} — {e}")
            session.rollback()

        session.commit()

    return courses

def pullCourses():
    print("Starting")
    courses = []
    driver = None
    try:
            service = Service(GeckoDriverManager().install())
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
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
                #print(parseElement(element.get_attribute("innerHTML")))
    except TimeoutException:
        driver.quit()
        return courses
    except Exception as e:
        traceback.print_exc()
    finally:
        if driver is not None:
            driver.quit()

@bp.route("/AddCourses", methods=["POST"])
@role_required("UAFS_ADMINS")
def addCourses():

    courses = pullCourses()
    return jsonify({
        "message": "Current courses addition completed.",
        "count": len(courses),
        "courses": courses
    })


@bp.route("/View/", methods=["POST"])
@role_required("UAFS_ADMINS", "UAFS_ADVISORS", "UAFS_STUDENTS")
def getCurrentCourses():
    try:
        semester = request.form.get('semester')
        with Session(engine) as session:
            courses = session.query(CurrentCourse.CurrentCourseMap).filter(CurrentCourse.CurrentCourseMap.academicperiod.contains(semester)).all()

            result = []
            for c in courses:
                result.append({
                    "section": c.section,
                    "courseavailability": c.courseavailability,
                    "deliverymode": c.deliverymode,
                    "meetingpattern": c.meetingpattern,
                    "courselocation": c.courselocation,
                    "instructor": c.instructor,
                    "capacity": c.capacity,
                    "enrolled": c.enrolled,
                    "academicperiod": c.academicperiod,
                    "startdate": c.startdate,
                })

            return jsonify({
                "count": len(result),
                "courses": result
            }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Failed to fetch current courses.", "error": str(e)}), 500