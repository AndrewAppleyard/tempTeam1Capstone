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


@app.route("/Admin/Advisor/Insert", methods = ['POST'])
def addAdvisor() -> None:
    advisor = Advisor.AdvisorMap()
    advisor.firstName = request.form.get('firstName')
    advisor.lastName = request.form.get('lastName')
    advisor.email = request.form.get('email')
    advisor.phoneNumber = request.form.get('phoneNumber')
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
            result = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap.advisorID == id).first()
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
            advisor = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap.advisorID == id).first()
            if(request.form.get('firstName') != None):
                advisor.firstName = request.form.get('firstName')
            if(request.form.get('lastName') != None):
                advisor.lastName = request.form.get('lastName')
            if(request.form.get('email') != None):
                advisor.email = request.form.get('email')
            if(request.form.get('phoneNumber') != None):
                advisor.phoneNumber = request.form.get('phoneNumber')
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
    student = Student.StudentMap()
    student.firstName = request.form.get('firstName')
    student.lastName = request.form.get('lastName')
    student.email = request.form.get('email')
    student.phoneNumber = request.form.get('phoneNumber')
    student.role = request.form.get('role')
    student.school = request.form.get('school')
    student.gpa = request.form.get('gpa')
    student.major = request.form.get('major')
    student.minor = request.form.get('minor')
    student.registrationStatus = request.form.get('registrationStatus')
    student.advisingStatus = request.form.get('advisingStatus')
    student.dateAdvised = request.form.get('dateAdvised')
    student.financialHold = request.form.get('financialHold')
    student.advisingHold = request.form.get('advisingHold')
    student.academicHold = request.form.get('academicHold')

    try:
        with Session(engine) as session:
            session.add(student)
            session.commit()
            session.refresh(student)
            session.close()

            return "Student Added"
    except Exception as e:
        traceback.print_exc()
        
        return "Student Add Failed"
    finally:
        pass

@app.route("/Admin/Student/<id>")
def deleteStudent(id: int):
   
    try:
        with Session(engine) as session:
            result = session.query(Student.StudentMap).filter(Student.StudentMap.studentID == id).first()
            session.delete(result)
            session.commit()
            return "Student Deleted"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Student Delete Failed"
    finally:
        session.close()

@app.route("/Admin/Student/Update/<id>", methods = ['GET', 'POST'])
def updateStudent(id: int) -> None:
    try:
        with Session(engine) as session:
            student = session.query(Student.StudentMap).filter(Student.StudentMap.StudentID == id).first()
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
                student.registrationStatus = request.form.get('registrationStatus')
            if(request.form.get('advisingStatus') != None):
                student.advisingStatus = request.form.get('advisingStatus')
            if(request.form.get('dateAdvised') != None):
                student.dateAdvised = request.form.get('dateAdvised')
            if(request.form.get('financialHold') != None):
                student.financialHold = request.form.get('financialHold')
            if(request.form.get('advisingHold') != None):
                student.advisingHold = request.form.get('advisingHold')
            if(request.form.get('academicHold') != None):
                student.academicHold = request.form.get('academicHold')

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
            admin.firstName = result.firstName
            admin.lastName = result.lastName
            admin.email = result.email
            admin.phoneNumber = result.phoneNumber
            admin.role = result.role
            admin.school = result.school

            return admin.__dict__
    except Exception as e:
        traceback.print_exc()
        return "Failed to Find Admin"
    finally:
        session.close()
app.run(host = "0.0.0.0", port=80)