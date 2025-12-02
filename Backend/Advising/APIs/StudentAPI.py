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
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from functools import wraps
from Advising.APIs import URL
from Advising.APIs.LDAPservice import updateUser

bp = Blueprint('StudentAPI', __name__, url_prefix="/Student")

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

from UserClasses import Advisor, User, Student, Admin

path = os.path.abspath(__file__)
directory = os.path.dirname(path)
databaseURL = URL.decrypt(directory + "/config/config.txt", directory + "/config/.gitignore.key")

engine = create_engine(databaseURL)
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

dateFormatString = "%Y-%m-%d"

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


@bp.route("/", methods=['GET'])
@role_required("UAFS_ADMINS")
def getStudents():
    '''token = get_jwt()
    if token["Role"] == "Student":
        print("Access succesful!")
    else:
        print("Can't access with current role.")
        return jsonify({"message":"Can't access with current role."}), 401'''
    
    try:
        with Session(engine) as session:

            studentList = []

            results = session.execute(session.query(Student.StudentMap)).scalars()

            for student in results:
                
                s = Student.Student()
                s.studentid = student.studentid
                s.firstname = student.firstname
                s.lastname = student.lastname
                s.email = student.email
                s.phonenumber = student.phonenumber
                s.role = student.role
                s.school = student.school
                s.gpa = student.gpa
                s.major = student.major
                s.majorconcentration = student.majorconcentration
                s.minor = student.minor
                s.classstanding = student.classstanding
                s.registrationstatus = student.registrationstatus
                s.advisingstatus = student.advisingstatus
                s.dateadvised = student.dateadvised
                s.financialhold = student.financialhold
                s.advisinghold = student.advisinghold
                s.academichold = student.academichold
                s.classes = student.classes

                studentList.append(s.__dict__)

            return studentList
        
    except Exception as e:
        
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()

@bp.route("/<int:studentid>",methods = ['GET', 'POST'])
@role_required("UAFS_STUDENTS", "UAFS_ADVISORS")
def getStudentInfo(studentid: int):

    try:
        with Session(engine) as session:
            studentData = Student.Student()

            result = session.query(Student.StudentMap) \
                    .filter(Student.StudentMap.studentid == studentid) \
                    .first()

            student = Student.Student()

            student.studentid = result.studentid
            student.firstname = result.firstname
            student.lastname = result.lastname
            student.email = result.email
            student.phonenumber = result.phonenumber
            student.role = result.role
            student.school = result.school
            student.gpa = result.gpa
            student.major = result.major
            student.majorconcentration = result.majorconcentration
            student.minor = result.minor
            student.classstanding = result.classstanding
            student.registrationstatus = result.registrationstatus
            student.advisingstatus = result.advisingstatus
            student.dateadvised = result.dateadvised
            student.finanicalHold = result.financialhold
            student.advisinghold = result.advisinghold
            student.academichold = result.academichold
            student.classes = result.classes

            return student.__dict__
    except Exception as e:
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()

@bp.route("/Update/<int:id>", methods = ['GET','POST'])
@role_required("UAFS_ADMINS", "UAFS_STUDENTS", "UAFS_ADVISORS")
def updateStudent(id: int) -> None:
    token = get_jwt()
    try:
        with Session(engine) as session:
            false = "false"
            true = "true"
            student = session.query(Student.StudentMap).filter(Student.StudentMap.studentid == id).first()

            oldEmail = student.email 
            oldFirstName = student.firstname 
            oldLastName = student.lastname

            if (token["Role"] == 'UAFS_STUDENTS'):
                if(request.form.get('phonenumber') != None):
                    student.phonenumber = request.form.get('phonenumber')
                    
            elif (token["Role"] == 'UAFS_ADVISORS'):
                if(request.form.get('major') != None):
                    student.major = request.form.get('major')
                if(request.form.get('majorconcentration') != None):
                    student.majorconcentration = request.form.get('majorconcentration')
                if(request.form.get('minor') != None):
                    student.minor = request.form.get('minor')
                if(request.form.get('classstanding') != None):
                    student.classstanding = request.form.get('classstanding')
                if(request.form.get('advisingstatus') != None):
                    if(request.form.get('advisingstatus').casefold() == true.casefold()):
                        student.advisingstatus = True
                    elif(request.form.get('advisingstatus').casefold() == false.casefold()):
                        student.advisingstatus = False
                if(request.form.get('dateadvised') != None):
                    date = datetime.strptime(request.form.get('dateadvised'), dateFormatString)
                    student.dateadvised = date
                if(request.form.get('advisinghold') != None):
                    if(request.form.get('advisinghold').casefold() == true.casefold()):
                        student.advisinghold = True
                    elif(request.form.get('advisinghold').casefold() == false.casefold()):
                        student.advisinghold = False

            elif (token["Role"] == 'UAFS_ADMINS'):
                if(request.form.get('firstname') != None):
                    student.firstname = request.form.get('firstname')
                if(request.form.get('lastname') != None):
                    student.lastname = request.form.get('lastname')
                if(request.form.get('email') != None):
                    student.email = request.form.get('email')
                if(request.form.get('role') != None):
                    student.role = request.form.get('role')
                if(request.form.get('phonenumber') != None):
                    student.phonenumber = request.form.get('phonenumber')
                if(request.form.get('school') != None):
                    student.school = request.form.get('school')
                if(request.form.get('major') != None):
                    student.major = request.form.get('major')
                if(request.form.get('majorconcentration') != None):
                    student.majorconcentration = request.form.get('majorconcentration')
                if(request.form.get('minor') != None):
                    student.minor = request.form.get('minor')
                if(request.form.get('classstanding') != None):
                    student.classstanding = request.form.get('classstanding')
                if(request.form.get('registrationstatus') != None):
                    if(request.form.get('registrationstatus').casefold() == true.casefold()):
                        student.registrationstatus = True
                    elif(request.form.get('registrationstatus').casefold() == false.casefold()):
                        student.registrationstatus = False
                if(request.form.get('financialhold') != None):
                    if(request.form.get('financialhold').casefold() == true.casefold()):
                        student.financialhold = True
                    elif(request.form.get('financialhold').casefold() == false.casefold()):
                        student.financialhold = False
                if(request.form.get('advisinghold') != None):
                    if(request.form.get('advisinghold').casefold() == true.casefold()):
                        student.advisinghold = True
                    elif(request.form.get('advisinghold').casefold() == false.casefold()):
                        student.advisinghold = False
                if(request.form.get('academichold') != None):
                    if(request.form.get('academichold').casefold() == true.casefold()):
                        student.academichold = True
                    elif(request.form.get('academichold').casefold() == false.casefold()):
                        student.academichold = False
            
            session.commit()

            if oldEmail != student.email or oldFirstName != student.firstname or oldLastName != student.lastname:
                try:
                    updateUser(oldEmail, student.email, student.firstname, student.lastname)
                except Exception as ex:
                    print("LDAP email update failed:", ex)

            return "Student Update Successful"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Student Update Failed"
    finally:
        session.close()

