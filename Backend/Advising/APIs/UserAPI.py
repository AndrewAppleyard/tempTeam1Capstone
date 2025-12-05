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
parent_dir = os.path.join(current_dir, "..")
sys.path.append(os.path.abspath(parent_dir))

bp = Blueprint('UserAPI', __name__, url_prefix='/User')

path = os.path.abspath(__file__)
directory = os.path.dirname(path)

databaseURL = URL.decrypt(directory + "/config/config.txt", directory + "/config/.gitignore.key")

engine = create_engine(databaseURL)
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from UserClasses import User, Advisor, Student

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

@bp.route("/GetUserByEmail/<string:email>", methods=['GET'])
@role_required("UAFS_ADMINS", "UAFS_ADVISORS", "UAFS_STUDENTS")
def resolveUserByEmail(email):
    try:
        with Session(engine) as session:
            user = session.query(User.UserMap).filter(User.UserMap.email == email).first()

            if not user:
                return jsonify({"error": "User not found"}), 404

            return jsonify({
                "userid": user.userid,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "role": user.role
            })

    except Exception as e:
        print("Resolve error:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500
    finally:
        session.close()

@bp.route("/GetAdvisorByUID/<int:userid>", methods=['GET'])
@role_required("UAFS_ADVISORS", "UAFS_ADMINS")
def resolveAdvisorByUID(userid):
    try:
        with Session(engine) as session:
            result = session.query(Advisor.AdvisorMap)\
                .join(User.UserMap, Advisor.AdvisorMap.email == User.UserMap.email)\
                .filter(User.UserMap.userid == userid).first()

            if not result:
                return jsonify({"error": "advisor not found"}), 404

            advisor = Advisor.Advisor()
            advisor.advisorid = result.advisorid

            return jsonify({
                "advisorid": advisor.advisorid
            })

    except Exception as e:
        print("Resolve error:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500
    finally:
        session.close()

@bp.route("/GetStudentByUID/<int:userid>", methods=['GET'])
@role_required("UAFS_STUDENTS", "UAFS_ADMINS")
def resolveStudentByUID(userid):
    try:
        with Session(engine) as session:
            result = session.query(Student.StudentMap)\
                .join(User.UserMap, Student.StudentMap.email == User.UserMap.email)\
                .filter(User.UserMap.userid == userid).first()

            if not result:
                return jsonify({"error": "student not found"}), 404

            student = Student.Student()
            student.studentid = result.studentid

            return jsonify({
                "studentid": student.studentid
            })

    except Exception as e:
        print("Resolve error:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500
    finally:
        session.close()