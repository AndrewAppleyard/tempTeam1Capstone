import sys
import os
import psycopg2

current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the adjacent folder
adjacent_folder_path = os.path.join(current_dir, '..')

# Insert the adjacent folder's path into sys.path
sys.path.insert(0, adjacent_folder_path)

from flask import Flask, jsonify, request, Blueprint
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
# from pymysql import install_as_MySQLdb
import json
import traceback
from datetime import datetime
from UserClasses import Advisor, User, Student, Admin
# import Advisor, User, Student, Admin


#bp = Blueprint('Admin', __name__, url_prefix='/Admin')

databaseURL = "postgresql+psycopg2://postgres:us3URownP4$sword8410@localhost:5432/advising"
engine = create_engine(databaseURL)

if not database_exists(engine.url):
    create_database(engine.url)
    print("Database has been created!\n")
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


base = User.Base.getBase()

base.metadata.create_all(bind=engine)

app = Flask(__name__)

dateFormatString = "%m-%d-%Y"

@app.route("/Admin/Advisor/Insert", methods = ['POST'])
def addAdvisor() -> None:
    advisor = Advisor.AdvisorMap()
    advisor.firstname = request.form.get('firstname')
    advisor.lastname = request.form.get('lastname')
    advisor.email = request.form.get('email')
    advisor.phonenumber = request.form.get('phonenumber')
    advisor.role = request.form.get('role')
    advisor.school = request.form.get('school')

    try:
        with Session(engine) as session:
            session.add(advisor)
            session.commit()
            session.refresh(advisor)

            return "Advisor Added"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        
        return "Advisor Add Failed"
    finally:
        session.close()
        

@app.route("/Admin/Advisor/<id>")
def deleteAdvisor(id: int):
   
    try:
        with Session(engine) as session:
            result = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap.advisorid == id).first()
            session.delete(result)
            session.commit()
            return "Advisor Deleted"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Advisor Delete Failed"
    finally:
        session.close()

@app.route("/Admin/Advisor/Update/<id>", methods = ['GET', 'POST'])
def updateAdvisor(id: int) -> None:
    try:
        with Session(engine) as session:
            advisor = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap.advisorid == id).first()
            if(request.form.get('firstname') != None):
                advisor.firstname = request.form.get('firstname')
            if(request.form.get('lastname') != None):
                advisor.lastname = request.form.get('lastname')
            if(request.form.get('email') != None):
                advisor.email = request.form.get('email')
            if(request.form.get('phonenumber') != None):
                advisor.phonenumber = request.form.get('phonenumber')
            if(request.form.get('role') != None):
                advisor.role = request.form.get('role')
            if(request.form.get('school') != None):
                advisor.school = request.form.get('school')

            session.commit()

            return "Advisor Update Successful"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Advisor Update Failed"
    finally:
        session.close()

@app.route("/Admin/Student/Insert", methods=['POST']) 
def addStudent():
    true = "True"
    false = "False"

    student = Student.StudentMap()
    student.firstname = request.form.get('firstname')
    student.lastname = request.form.get('lastname')
    student.email = request.form.get('email')
    student.phonenumber = request.form.get('phonenumber')
    student.role = request.form.get('role')
    student.school = request.form.get('school')
    student.gpa = request.form.get('gpa')
    student.major = request.form.get('major')
    student.minor = request.form.get('minor')

    if(request.form.get('registrationStatus').casefold() == true.casefold()):
        student.registrationStatus = True
    elif(request.form.get('registrationStatus').casefold() == false.casefold()):
        student.registrationStatus = False
    if(request.form.get('advisingStatus').casefold() == true.casefold()):
        student.advisingStatus = True
    elif(request.form.get('advisingStatus').casefold() == false.casefold()):
        student.advisingStatus = False
    if(request.form.get('dateAdvised') != None):
        date = datetime.strptime(request.form.get('dateAdvised'), dateFormatString)
        student.dateAdvised = date
    if(request.form.get('financialHold').casefold() == true.casefold()):
        student.financialHold = True
    elif(request.form.get('financialHold').casefold() == false.casefold()):
        student.financialHold = False
    if(request.form.get('advisingHold').casefold() == true.casefold()):
        student.advisingHold = True
    elif(request.form.get('advisingHold').casefold() == false.casefold()):
        student.advisingHold = False
    if(request.form.get('academicHold').casefold() == true.casefold()):
        student.academicHold = True
    elif(request.form.get('academicHold').casefold() == false.casefold()):
        student.academicHold = False

    try:
        with Session(engine) as session:
            session.add(student)
            session.commit()
            session.refresh(student)

            return "Student Added"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Student Add Failed"
    finally:
        session.close()

@app.route("/Admin/Student/<id>")
def deleteStudent(id: int):
   
    try:
        with Session(engine) as session:
            result = session.query(Student.StudentMap).filter(Student.StudentMap.studentid == id).first()
            session.delete(result)
            session.commit()
            return "Student Deleted"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Student Delete Failed"
    finally:
        session.close()

@app.route("/Admin/Student/Update/<id>/<role>", methods = ['GET', 'POST'])
def updateStudent(id: int, role: str) -> None:
    try:
        true = "True"
        flase = "False"
        with Session(engine) as session:
            student = session.query(Student.StudentMap).filter(Student.StudentMap.studentid == id).first()
            if(request.form.get('firstname') != None):
                student.firstname = request.form.get('firstname')
            if(request.form.get('lastname') != None):
                student.lastname = request.form.get('lastname')
            if(request.form.get('email') != None):
                student.email = request.form.get('email')
            if(request.form.get('phonenumber') != None):
                student.phonenumber = request.form.get('phonenumber')
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
                status = request.form.get('registrationStatus')
                if(status.casefold() == true.casefold()):
                    student.registrationStatus = True
                elif(status.casefold() == false.casefold()):
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
                hold = request.form.get('financialHold')
                if(hold.casefold() == true.casefold()):
                    student.financialHold = True
                elif(hold.casefold() == false.casefold()):
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

@app.route("/Admin/<id>")
def getAdmin(id: int):
    try:
        with Session(engine) as session:
            result = session.query(Admin.AdminMap).filter(Admin.AdminMap.adminID == id).first()
            admin = Admin.Admin()

            admin.adminID= result.adminID
            admin.firstname = result.firstname
            admin.lastname = result.lastname
            admin.email = result.email
            admin.phonenumber = result.phonenumber
            admin.role = result.role
            admin.school = result.school

            return admin.__dict__
    except Exception as e:
        traceback.print_exc()
        return "Failed to Find Admin"
    finally:
        session.close()


@app.route("/Admin/Student/Advisor", methods=['POST'])
def addStudentToAdvisor():
    advisorAndStudents = Advisor.Advisor_And_StudentsMap()
    advisorAndStudents.advisorid = request.form.get('advisorid')
    advisorAndStudents.studentid = request.form.get('studentid')

    try:
        with Session(engine) as session:
            session.add(advisorAndStudents)
            session.commit()
            session.refresh(advisorAndStudents)

            return "Student Added to Advisor"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        
        return "Failed to Add Student to Advisor"
    finally:
        session.close()

@app.route("/Admin/Student/Advisor/<studentid>/<advisorid>")
def removeStudentFromAdvisor(studentid: int, advisorid: int):
    try:
        with Session(engine) as session:
            result = session.query(Advisor.Advisor_And_StudentsMap).filter(Advisor.Advisor_And_StudentsMap.advisorid == advisorid).filter(Advisor.Advisor_And_StudentsMap.studentid == studentid).first()
            session.delete(result)
            session.commit()
            return "Student Removed From Advisor"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Failed to Remove Student From Advisor"
    finally:
        session.close()

app.run(host = "0.0.0.0", port=80)