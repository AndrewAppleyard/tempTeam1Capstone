import sys
import os
import psycopg2

current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the adjacent folder
adjacent_folder_path = os.path.join(current_dir, '..')

# Insert the adjacent folder's path into sys.path
sys.path.insert(0, adjacent_folder_path)

from flask import Flask, jsonify, request
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
# from pymysql import install_as_MySQLdb
import json
import traceback
from datetime import datetime
from UserClasses import Advisor, User, Student, Admin
# import Advisor, User, Student, Admin

databaseURL = "postgresql+psycopg2://postgres:us3URownP4$sword8410@localhost:5432/advising"
engine = create_engine(databaseURL)

if not database_exists(engine.url):
    create_database(engine.url)
    print("Database has been created!\n")
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base = User.Base.getBase()

base.metadata.create_all(bind=engine)

app = Flask(__name__)

@app.route("/Advisor/")
def getAdvisors():
    try:
        with Session(engine) as session:
            advisorData = Advisor.Advisor()
            advisorList = []
            
            results = session.execute(session.query(Advisor.AdvisorMap)).scalars()

            for advisor in results:
                a = Advisor.Advisor()
                a.userid = advisor.advisorid
                a.firstname = advisor.firstname
                a.lastname = advisor.lastname
                a.email = advisor.email
                a.phonenumber = advisor.phonenumber
                a.role = advisor.role
                a.school = advisor.school

                advisorList.append(a)

            return advisorList

    except Exception as e:
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()

@app.route("/Advisor/<advisorid>", methods= ['GET', 'POST'] )
def getAdvisor(advisorid: int):
    try:
        with Session(engine) as session:
            result = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap == advisorid).first()
            
            advisor = Advisor.Advisor()

            advisor.advisorid = result.advisorid
            advisor.firstname = result.firstname
            advisor.lastname = result.lastname
            advisor.email = result.email
            advisor.phonenumber = result.phonenumber
            advisor.role = result.role
            advisor.school = result.school

            return advisor.__dict__
    except Exception as e:
        traceback.print_exc()
        return "Failed to Find Advisor"
    finally:
        session.close()

@app.route("/Advisor/Student/<advisorid>")
def getAdvisorStudents():
    try:
        s = Student.Student()
        with Session(engine) as session:
            results = scalars((
            session.query(Student)
            .join(AdvisorAndStudents, Student.studentid == AdvisorAndStudents.studentid)
            .filter(AdvisorAndStudents.advisorid == advisor_id)
            .all())
            )

        for student in results:
            s.userid = student.studentid
            s.firstname = student.firstname
            s.lastname = student.lastname
            s.email = student.email
            s.role = student.role
            s.school = student.school
            s.gpa = student.gpa
            s.major = student.major
            s.minor = student.minor
            s.registrationStatus = student.registrationStatus
            s.advisingStatus = student.advisingStatus
            s.dateAdvised = student.dateAdvised
            s.financialHold = student.financialHold
            s.advisingHold = student.advisingHold
            s.academicHold = student.academicHold
    except Exception as e:
        traceback.print_exc()
        return "Failed to Get Students"
    finally:
        session.close()