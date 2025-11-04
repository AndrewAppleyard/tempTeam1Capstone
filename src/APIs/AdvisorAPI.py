from flask import Flask, jsonify, request
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
import traceback
from datetime import datetime
import sys
import os

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

from UserClasses import Advisor, User, Student, Admin
for paths in sys.path:
     print(paths)

databaseURL = "mysql+pymysql://user:pass@localhost:3306/Test"
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
                a.userID = advisor.advisorID
                a.firstName = advisor.firstName
                a.lastName = advisor.lastName
                a.email = advisor.email
                a.phoneNumber = advisor.phoneNumber
                a.role = advisor.role
                a.school = advisor.school

                advisorList.append(a)

            return advisorList

    except Exception as e:
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()

@app.route("/Advisor/<advisorID>", methods= ['GET', 'POST'] )
def getAdvisor(advisorID: int):
    try:
        with Session(engine) as session:
            result = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap == advisorID).first()
            
            advisor = Advisor.Advisor()

            advisor.advisorID = result.advisorID
            advisor.firstName = result.firstName
            advisor.lastName = result.lastName
            advisor.email = result.email
            advisor.phoneNumber = result.phoneNumber
            advisor.role = result.role
            advisor.school = result.school

            return advisor.__dict__
    except Exception as e:
        traceback.print_exc()
        return "Failed to Find Advisor"
    finally:
        session.close()

@app.route("/Advisor/Student/<advisorID>")
def getAdvisorStudents():
    try:
        s = Student.Student()
        with Session(engine) as session:
            results = scalars((
            session.query(Student.StudentMap)
            .join(Advisor.Advisor_And_StudentsMap, Student.studentID == Advisor.Advisor_And_StudentsMap.studentID)
            .filter(Advisor.Advisor_And_StudentsMap.advisorID == Advisor.advisorID)
            .all())
    )

        for student in results:
            s.userID = student.studentID
            s.firstName = student.firstName
            s.lastName = student.lastName
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