from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import traceback
from datetime import datetime
import os, sys
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from functools import wraps
from Advising.APIs import URL
from UserClasses import Student, User

#TODO: Currently throws 500 error because theres something wrong with the logic
bp = Blueprint('AgentAPI', __name__, url_prefix="/Schedule")

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

path = os.path.abspath(__file__)
directory = os.path.dirname(path)
databaseURL = URL.decrypt(directory + "/config/config.txt", directory + "/config/.gitignore.key")

engine = create_engine(databaseURL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

#put the student id after generate schedule
@bp.route("/GenerateSchedule", methods=["POST"])
@role_required("UAFS_STUDENTS")
def generate_schedule():
    try:    
        #hardcoded, will be replaced with a agent component
        data = {
            "student_id": "1",
            "name": "Andrew Appleyard",
            "semester": "Spring 2026",
            "courses": [
                {
                    "code": "CSCE 30003-0001",
                    "title": "Distributed Systems",
                    "credits": 3,
                    "delivery_mode": "In-Person",
                    "meeting_pattern": "Monday/Wednesday | 2:00 PM - 3:15 PM",
                    "location": "UAFS | Baldor Tech Computer Lab-BD147",
                    "instructor": "Israel B Cuevas"
                },
                {
                    "code": "CSCE 30503-0001",
                    "title": "Operating Systems",
                    "credits": 3,
                    "delivery_mode": "In-Person",
                    "meeting_pattern": "Tuesday/Thursday | 2:00 PM - 3:15 PM",
                    "location": "UAFS | Baldor Tech Computer Lab-BD144",
                    "instructor": "Brian Paul McLaughlan"
                },
                {
                    "code": "CSCE 31103-0001",
                    "title": "Artificial Intelligence",
                    "credits": 3,
                    "delivery_mode": "In-Person",
                    "meeting_pattern": "Tuesday/Thursday | 9:30 AM - 10:45 AM",
                    "location": "UAFS | Baldor Tech Computer Lab-BD147",
                    "instructor": "Israel B Cuevas"
                },
                {
                    "code": "GEN_ED FA/Hum/SocSci",
                    "title": "Fine Arts/Humanities/Social Sciences requirement",
                    "credits": 3,
                    "delivery_mode": "Online/Variable",
                    "meeting_pattern": "To Be Determined",
                    "location": "UAFS",
                    "instructor": "TBD"
                },
                {
                    "code": "CSCE 43733-9001",
                    "title": "Information Retrieval",
                    "credits": 3,
                    "delivery_mode": "In-Person",
                    "meeting_pattern": "Tuesday/Thursday | 6:50 PM - 8:05 PM",
                    "location": "UAFS | Baldor Tech Computer Lab-BD147",
                    "instructor": "Andrew Lee Mackey"
                }
            ]
        }

        with Session(engine) as session:
            student = session.query(Student.StudentMap).filter(Student.StudentMap.studentid == student_id).first()

            if not student:
                return jsonify({"message": "Student not found."}), 404

            student.classes = data["courses"]

            session.commit()

            return jsonify({
                "message": "Successfully generated schedule.",
                "studentid": student.studentid,
                "num_courses": len(data["courses"]),
                "timestamp": datetime.now().isoformat()
            }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Failed to generate schedule.", "error": str(e)}), 500