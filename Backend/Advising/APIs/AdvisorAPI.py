from flask import Flask, jsonify, request, Blueprint, url_for
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
import traceback
import sys
import os
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from functools import wraps
from Advising.APIs import URL
import requests

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

bp = Blueprint('AdvisorAPI', __name__, url_prefix='/Advisor')

from UserClasses import Advisor, User, Student, Admin

path = os.path.abspath(__file__)
directory = os.path.dirname(path)

databaseURL = URL.decrypt(directory + "/config/config.txt", directory + "/config/.gitignore.key")

engine = create_engine(databaseURL)
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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

                advisorList.append(a.__dict__)

            return jsonify(advisorList)

    except Exception as e:
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()

@bp.route("/<int:advisorid>", methods= ['GET'] )
@role_required("UAFS_ADVISORS", "UAFS_ADMINS")
def getAdvisor(advisorid: int):
    try:
        with Session(engine) as session:
            result = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap.advisorid == advisorid).first()
            
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

@bp.route("/Student/<int:advisorid>")
@role_required("UAFS_ADVISORS", "UAFS_ADMINS")
def getAdvisorStudents(advisorid: int):
    try:
        with Session(engine) as session:
            statement = (
            select(Student.StudentMap)
            .join(Advisor.Advisor_And_StudentsMap, Student.StudentMap.studentid == Advisor.Advisor_And_StudentsMap.studentid)
            .filter(Advisor.Advisor_And_StudentsMap.advisorid == advisorid)
        )
        results = session.scalars(statement).all()

        students = []
        for student in results:
            s = Student.Student()
            s.userid = student.studentid
            s.firstname = student.firstname
            s.lastname = student.lastname
            s.email = student.email
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
            s.classes = student.classes
            students.append(s.__dict__)

        return students
            
    except Exception as e:
        traceback.print_exc()
        return "Failed to Get Students"
    finally:
        session.close()

@bp.route("/ByStudent/<studentid>")
@role_required("UAFS_ADVISORS", "UAFS_ADMINS", "UAFS_STUDENTS")
def getAdvisorByStudent(studentid: int):
    try:
        with Session(engine) as session:
            statement = (
                select(Advisor.AdvisorMap)
                .join(Advisor.Advisor_And_StudentsMap, Advisor.AdvisorMap.advisorid == Advisor.Advisor_And_StudentsMap.advisorid)
                .filter(Advisor.Advisor_And_StudentsMap.studentid == studentid)
            )

            result = session.scalars(statement).first()

            if not result:
                return jsonify(None), 200

            advisor = Advisor.Advisor()
            advisor.userid = result.advisorid
            advisor.firstname = result.firstname
            advisor.lastname = result.lastname
            advisor.email = result.email
            advisor.phonenumber = result.phonenumber
            advisor.role = result.role
            advisor.school = result.school

            return jsonify(advisor.__dict__), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Failed to find advisor for student"}), 500

    finally:
        session.close()
