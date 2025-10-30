from flask import Blueprint, Flask, jsonify, request
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
import traceback
from datetime import datetime
import os, sys
from ldap3 import Server, Connection, ALL
from flask_jwt_extended import jwt_required, get_jwt

bp = Blueprint('AdvisorAPI', __name__, url_prefix="/Student")

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

from UserClasses import Advisor, User, Student, Admin

databaseURL = "mysql+pymysql://User:pass@localhost:3306/test"
# Change User to user and test to Test when pushing
# Chop Student off of any urls and convert to blueprint using the Robert isntructions from Discord
engine = create_engine(databaseURL)

LDAP_SERVER = "ldap://localhost:389"
LDAP_BASE_DN = "dc=example,dc=com"
LDAP_USER_DN_FORMAT = "uid={}, ou=People," + LDAP_BASE_DN

if not database_exists(engine.url):
    create_database(engine.url)
    print("Database has been created!\n")
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base = User.Base.getBase()

base.metadata.create_all(bind=engine)

#app = Flask(__name__)

dateFormatString = "%Y-%m-%d"

@bp.route("", methods=['GET'])
@jwt_required()
def getStudents():
    token = get_jwt()
    if token["Role"] == "Student":
        print("Student route here!")
        return jsonify({"message":"Student route here!"}), 200
    else:
        print("Can't access with current role.")
        return jsonify({"message":"Can't access with current role."}), 401
    
    try:
        with Session(engine) as session:

            studentList = []

            results = session.execute(session.query(Student.StudentMap)).scalars()

            for student in results:
                
                s = Student.Student()
                s.studentID = student.studentID
                s.firstName = student.firstName
                s.lastName = student.lastName
                s.email = student.email
                s.phoneNumber = student.phoneNumber
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

                studentList.append(s.__dict__)

            return studentList
        
    except Exception as e:
        
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()

@bp.route("/<studentID>",methods = ['GET', 'POST'])
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

@bp.route("/Admin/Update/<id>/<role>", methods = ['GET','POST'])
def updateStudent(id: int, role: str) -> None:
    try:
        with Session(engine) as session:
            false = "false"
            true = "true"
            student = session.query(Student.StudentMap).filter(Student.StudentMap.studentID == id).first()
            if(request.form.get('firstName') != None):
                student.firstName = request.form.get('firstName')
            if(request.form.get('lastName') != None):
                student.lastName = request.form.get('lastName')
            if(request.form.get('email') != None):
                student.email = request.form.get('email')
            if(request.form.get('phoneNumber') != None):
                student.phoneNumber = request.form.get('phoneNumber')
            if(request.form.get('role') != None):
                student.role = request.form.get('role')
            if(request.form.get('school') != None):
                student.school = request.form.get('school')
            if(request.form.get('gpa') != None):
                student.gpa = request.form.get('gpa')
            if(request.form.get('major') != None):
                student.major = request.form.get('major')
            if(request.form.get('minor') != None):
                student.minor = request.form.get('minor')
            if(request.form.get('registrationStatus') != None):
                if(request.form.get('registrationStatus').casefold() == true.casefold()):
                    student.registrationStatus = True
                elif(request.form.get('registrationStatus').casefold() == false.casefold()):
                    student.registrationStatus = False
            if(request.form.get('advisingStatus') != None):
                if(request.form.get('advisingStatus').casefold() == true.casefold()):
                    student.advisingStatus = True
                elif(request.form.get('advisingStatus').casefold() == false.casefold()):
                    student.advisingStatus = False
            if(request.form.get('dateAdvised') != None):
                date = datetime.strptime(request.form.get('dateAdvised'), dateFormatString)
                student.dateAdvised = date
            if(request.form.get('financialHold') != None):
               if(request.form.get('financialHold').casefold() == true.casefold()):
                    student.financialHold = True
            elif(request.form.get('financialHold').casefold() == false.casefold()):
                    student.financialHold = False
            if(request.form.get('advisingHold') != None):
                if(request.form.get('advisingHold').casefold() == true.casefold()):
                    student.advisingHold = True
                elif(request.form.get('advisingHold').casefold() == false.casefold()):
                    student.advisingHold = False
            if(request.form.get('academicHold') != None):
                if(request.form.get('academicHold').casefold() == true.casefold()):
                    student.academicHold = True
                elif(request.form.get('academicHold').casefold() == false.casefold()):
                    student.academicHold = False

            session.commit()

            return "Student Update Successful"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Student Update Failed"
    finally:
        session.close()