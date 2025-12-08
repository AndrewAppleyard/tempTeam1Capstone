from flask import Flask, jsonify, request, Blueprint
from sqlalchemy import Column, Integer, String, create_engine, select, text
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
import traceback
from datetime import datetime
import sys
import os
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from functools import wraps
from UserClasses import Advisor, User, Student, Admin
from Advising.APIs import URL
from Advising.APIs.LDAPservice import addUser, deleteUser, updateUser

bp = Blueprint('AdminAPI', __name__, url_prefix='/Admin')

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


@bp.route("/Advisor/Insert", methods = ['POST'])
@role_required("UAFS_ADMINS")
def addAdvisor() -> None:
    advisor = Advisor.AdvisorMap()
    advisor.firstname = request.form.get('firstname')
    advisor.lastname = request.form.get('lastname')
    advisor.email = request.form.get('email')
    advisor.phonenumber = request.form.get('phonenumber')
    advisor.role = request.form.get('role')
    advisor.school = request.form.get('school')
    advisor.advisortype = request.form.get('advisortype')

    try:
        with Session(engine) as session:
            session.add(advisor)
            session.commit()
            session.refresh(advisor)

            try:
                addUser(advisor.email, advisor.firstname, advisor.lastname, "advisor")
            except Exception as ex:
                print("LDAP insert failed:", ex)

            return "Advisor Added"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        
        return "Advisor Add Failed"
    finally:
        session.close()

@bp.route("/Advisor/<int:id>", methods=['GET','POST'])
@role_required("UAFS_ADMINS")
def deleteAdvisor(id: int):
   
    try:
        with Session(engine) as session:
            result = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap.advisorid == id).first()
            email = result.email

            session.delete(result)
            session.commit()

            try:
                deleteUser(email)
            except:
                print("LDAP delete failed")

            return "Advisor Deleted"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Advisor Delete Failed"
    finally:
        session.close()

@bp.route("/Advisor/Update/<int:id>", methods = ['GET', 'POST'])
@role_required("UAFS_ADMINS")
def updateAdvisor(id: int) -> None:
    try:
        with Session(engine) as session:
            advisor = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap.advisorid == id).first()
            oldEmail = advisor.email
            oldFirstName = advisor.firstname
            oldLastName = advisor.lastname

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
            if(request.form.get('advisortype') != None):
                advisor.advisortype = request.form.get('advisortype')

            session.commit()

            if oldEmail != advisor.email or oldFirstName != advisor.firstname or oldLastName != advisor.lastname:
                try:
                    updateUser(oldEmail, advisor.email, advisor.firstname, advisor.lastname)
                except Exception as ex:
                    print("LDAP email update failed:", ex)

            return "Advisor Update Successful"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Advisor Update Failed"
    finally:
        session.close()

@bp.route("/Student/Insert", methods=['POST']) 
@role_required("UAFS_ADMINS")
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
    student.majorconcentration = request.form.get('majorconcentration')
    student.minor = request.form.get('minor')
    student.classstanding = request.form.get('classstanding')

    if(request.form.get('registrationstatus').casefold() == true.casefold()):
        student.registrationstatus = True
    elif(request.form.get('registrationstatus').casefold() == false.casefold()):
        student.registrationstatus = False
    if(request.form.get('advisingstatus').casefold() == true.casefold()):
        student.advisingstatus = True
    elif(request.form.get('advisingstatus').casefold() == false.casefold()):
        student.advisingstatus = False

    date_str = request.form.get('dateadvised')
    if date_str:
        student.dateadvised = datetime.strptime(date_str, dateFormatString)
    else:
        student.dateadvised = None
        
    if(request.form.get('financialhold').casefold() == true.casefold()):
        student.financialhold = True
    elif(request.form.get('financialhold').casefold() == false.casefold()):
        student.financialhold = False
    if(request.form.get('advisinghold').casefold() == true.casefold()):
        student.advisinghold = True
    elif(request.form.get('advisinghold').casefold() == false.casefold()):
        student.advisinghold = False
    if(request.form.get('academichold').casefold() == true.casefold()):
        student.academichold = True
    elif(request.form.get('academichold').casefold() == false.casefold()):
        student.academichold = False
    if(request.form.get('activestatus').casefold() == true.casefold()):
        student.activestatus = True
    elif(request.form.get('activestatus').casefold() == false.casefold()):
        student.activestatus = False

    try:
        with Session(engine) as session:
            session.add(student)
            session.commit()
            session.refresh(student)

            try:
                addUser(student.email, student.firstname, student.lastname, "student")
            except Exception as ex:
                print("LDAP insert failed:", ex)

            return jsonify({
                "studentid": student.studentid
            }), 201

    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return jsonify({
            "error": "Student Add Failed"
        }), 500

@bp.route("/Student/<int:id>", methods=['POST'])
@role_required("UAFS_ADMINS")
def deleteStudent(id: int):
   
    try:
        with Session(engine) as session:
            result = session.query(Student.StudentMap).filter(Student.StudentMap.studentid == id).first()
            email = result.email
            session.delete(result)
            session.commit()

            try:
                deleteUser(email)
            except:
                print("LDAP delete failed")
                
            return "Student Deleted"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return "Student Delete Failed"
    finally:
        session.close()

@bp.route("/<int:id>", methods=['GET','POST'])
@role_required("UAFS_ADMINS")
def getAdmin(id: int):
    try:
        with Session(engine) as session:
            result = session.query(Admin.AdminMap).filter(Admin.AdminMap.adminid == id).first()
            admin = Admin.Admin()

            admin.adminid = result.adminid
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

@bp.route("/Student/Advisor", methods=['POST'])
@role_required("UAFS_ADMINS")
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

@bp.route("/Student/Advisor/<int:studentid>/<int:advisorid>", methods=['GET'])
@role_required("UAFS_ADMINS")
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
