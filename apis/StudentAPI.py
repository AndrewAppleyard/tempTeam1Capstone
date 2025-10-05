from flask import Flask, jsonify, request
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
import traceback
from datetime import datetime
from UserClasses import Advisor, User, Student, Admin

databaseURL = "mysql+pymysql://User:pass@localhost:3306/Test"
engine = create_engine(databaseURL)

if not database_exists(engine.url):
    create_database(engine.url)
    print("Database has been created!\n")
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base = User.Base.getBase()

base.metadata.create_all(bind=engine)

app = Flask(__name__)

@app.route("/Student/<studentID>")
def getStudentInfo(studentID: int):

    try:
        with Session(engine) as session:
            studentData = Student.Student()

            result = session.query(Student.StudentMap) \
                    .filter(Student.StudentMap.studentID == studentID) \
                    .first()

            student = Student.Student()

            student.studentID = result.studentID
            student.firstName = result.firstName
            student.lastName = result.lastName
            student.email = result.email
            student.phoneNumber = result.phoneNumber
            student.role = result.role
            student.school = result.school
            student.gpa = result.gpa
            student.major = result.major
            student.minor = result.minor
            student.registrationStatus = result.registrationStatus
            student.advisingStatus = result.advisingStatus
            student.dateAdvised = result.dateAdvised
            student.finanicalHold = result.financialHold
            student.advisingHold = result.advisingHold
            student.academicHold = result.academicHold

            return student.__dict__
    except Exception as e:
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()