from flask import Blueprint, Flask, jsonify, request
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
import traceback
from datetime import datetime
import os, sys
from Advising.APIs import URL

bp = Blueprint('StudentAPI', __name__, url_prefix="/Student")

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

from UserClasses import Advisor, User, Student, Admin

# databaseURL = URL.decrypt("APIs/config/config.txt", "APIs/config/.gitignore.key")
databaseURL = "postgresql+psycopg2://postgres:us3URownP4$sword8410@localhost:5432/advising"

engine = create_engine(databaseURL)

if not database_exists(engine.url):
    create_database(engine.url)
    print("Database has been created!\n")
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base = User.Base.getBase()

base.metadata.create_all(bind=engine)

dateFormatString = "%Y-%m-%d"

@bp.route("/", methods=['GET'])
def getStudents():
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
                s.minor = student.minor
                s.registrationstatus = student.registrationstatus
                s.advisingstatus = student.advisingstatus
                s.dateadvised = student.dateadvised
                s.financialhold = student.financialhold
                s.advisinghold = student.advisinghold
                s.academichold = student.academichold

                studentList.append(s.__dict__)

            return studentList
        
    except Exception as e:
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()

@bp.route("/<studentid>",methods = ['GET', 'POST'])
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
            student.minor = result.minor
            student.registrationstatus = result.registrationstatus
            student.advisingstatus = result.advisingstatus
            student.dateadvised = result.dateadvised
            student.finanicalHold = result.financialhold
            student.advisinghold = result.advisinghold
            student.academichold = result.academichold

            return student.__dict__
    except Exception as e:
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()

@bp.route("/Update/<int:id>/<role>", methods = ['GET','POST'])
def updateStudent(id: int, role: str) -> None:
    try:
        with Session(engine) as session:
            false = "false"
            true = "true"
            student = session.query(Student.StudentMap).filter(Student.StudentMap.studentid == id).first()

            if (role.casefold() == 'student'):
                if(request.form.get('phonenumber') != None):
                    student.phonenumber = request.form.get('phonenumber')
                    
            elif (role.casefold() == 'advisor'):
                if(request.form.get('major') != None):
                    student.major = request.form.get('major')
                if(request.form.get('minor') != None):
                    student.minor = request.form.get('minor')
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

            elif (role.casefold() == 'admin'):
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
                if(request.form.get('minor') != None):
                    student.minor = request.form.get('minor')
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

            return "Student Update Successful"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Student Update Failed"
    finally:
        session.close()