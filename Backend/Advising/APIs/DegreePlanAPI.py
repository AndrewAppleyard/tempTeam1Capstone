from flask import Blueprint, jsonify
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import traceback, os, sys, json
from datetime import datetime
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from functools import wraps
from Advising.APIs import URL
from UserClasses import DegreePlan, User

bp = Blueprint("DegreePlanAPI", __name__, url_prefix="/DegreePlan")

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, "..")
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

data = {
    "degree": "B.S. in Computer Science",
    "institution": "University of Arkansas - Fort Smith",
    "major_code": "1054",
    "credit_hours_total": 120,
    "notes": [
        "At least 40 hours must be upper-level.",
        "Students must select one concentration of 9 hours."
    ],
    "core_courses": [
        {
            "year": "Freshman Fall",
            "courses": [
                { "code": "ENGL ___", "title": "English Composition I", "hours": 3 },
                { "code": "MATH 2804", "title": "Calculus I", "hours": 4 },
                { "code": "CS 1093", "title": "Computer Science Concepts", "hours": 3 },
                { "code": "GEN_ED FA/Hum/SocSci", "title": "Fine Arts/Humanities/Social Sciences requirement", "hours": 3 },
                { "code": "STEM 1001", "title": "College Prep for STEM Majors", "hours": 1 }
            ]
        },
        {
            "year": "Freshman Spring",
            "courses": [
                { "code": "ENGL ___", "title": "English Composition II", "hours": 3 },
                { "code": "MATH 2854", "title": "Calculus II", "hours": 4 },
                { "code": "CS 1014", "title": "Foundations of Programming I", "hours": 4 },
                { "code": "CS 1044", "title": "Foundations of Networking", "hours": 4 }
            ]
        },
        {
            "year": "Sophomore Fall",
            "courses": [
                { "code": "LABSCI ___", "title": "Lab Science requirement", "hours": 4 },
                { "code": "CS 2053", "title": "Foundations of CyberSecurity", "hours": 3 },
                { "code": "CS 1024", "title": "Foundations of Programming II", "hours": 4 },
                { "code": "CS ___ (1000-2000 level)", "title": "Lower-level CS elective", "hours": 3 },
                { "code": "FIN 1521", "title": "Personal Finance Applications", "hours": 1 }
            ]
        },
        {
            "year": "Sophomore Spring",
            "courses": [
                { "code": "LABSCI ___", "title": "Lab Science requirement", "hours": 4 },
                { "code": "MATH 2443", "title": "Discrete Mathematics I", "hours": 3 },
                { "code": "CS 2033", "title": "Web Systems", "hours": 3 },
                { "code": "CS 2003", "title": "Data Structures", "hours": 3 },
                { "code": "SPCH 1203", "title": "Intro to Speech Communication", "hours": 3 }
            ]
        },
        {
            "year": "Junior Fall",
            "courses": [
                { "code": "MATH 3303", "title": "Discrete Mathematics II", "hours": 3 },
                { "code": "CS 3033", "title": "Computer Architecture", "hours": 3 },
                { "code": "CS 3043", "title": "Database Systems", "hours": 3 },
                { "code": "CS 3103", "title": "Algorithms", "hours": 3 },
                { "code": "Concentration or CS/MATH/STAT elective", "title": "Elective", "hours": 3 }
            ]
        },
        {
            "year": "Junior Spring",
            "courses": [
                { "code": "CS 3003", "title": "Distributed Systems", "hours": 3 },
                { "code": "CS 3053", "title": "Operating Systems", "hours": 3 },
                { "code": "CS 3113", "title": "Artificial Intelligence", "hours": 3 },
                { "code": "GEN_ED FA/Hum/SocSci", "title": "Fine Arts/Humanities/Social Sciences requirement", "hours": 3 },
                { "code": "Concentration or CS/MATH/STAT elective", "title": "Elective", "hours": 3 }
            ]
        },
        {
            "year": "Senior Fall",
            "courses": [
                { "code": "GEN_ED FA/Hum/SocSci", "title": "Fine Arts/Humanities/Social Sciences requirement", "hours": 3 },
                { "code": "CS 4003", "title": "Software Engineering", "hours": 3 },
                { "code": "CS 4033", "title": "Ethics and Professional Practice", "hours": 3 },
                { "code": "HIST/GOVT ___", "title": "History/Government requirement", "hours": 3 },
                { "code": "Concentration or CS/MATH/STAT elective", "title": "Elective", "hours": 3 }
            ]
        },
        {
            "year": "Senior Spring",
            "courses": [
                { "code": "GEN_ED FA/Hum/SocSci", "title": "Fine Arts/Humanities/Social Sciences requirement", "hours": 3 },
                { "code": "Concentration or CS/MATH/STAT elective", "title": "Elective", "hours": 3 },
                { "code": "CS 4023", "title": "Senior Capstone", "hours": 3 },
                { "code": "CS 4043", "title": "Formal Languages", "hours": 3 },
                { "code": "MATH/STAT upper-level elective", "title": "Elective", "hours": 3 }
            ]
        }
    ],
    "concentrations": [
        {
            "code": "C037",
            "name": "CyberSecurity",
            "required_hours": 9,
            "courses": [
                "CS 3513 Applied Cryptography",
                "CS 3523 Computer Forensics",
                "CS 4213 Identity Management",
                "CS 4503 CyberOps",
                "CS 4523 Cyber Crimes"
            ],
            "notes": "Select any three courses from this list."
        },
        {
            "code": "C039",
            "name": "General",
            "required_hours": 9,
            "courses": "Any three upper-level CS elective courses with advisor approval",
            "notes": "General concentration gives flexibility."
        },
        {
            "code": "C051",
            "name": "Data Science & Artificial Intelligence",
            "required_hours": 9,
            "courses": [
                "CS 3323 Computer Graphics",
                "CS 3333 Big Data",
                "CS 4143 Deep Learning",
                "CS 4153 Advanced Algorithms",
                "CS 4323 Data Analytics",
                "CS 4333 Machine Learning",
                "CS 4343 Natural Language Processing",
                "CS 4363 Internet of Things Development",
                "CS 4373 Information Retrieval"
            ],
            "notes": "Select any three courses from this list."
        }
    ]
}

@bp.route("/UpdateDegreePlans", methods=["POST"])
@role_required("UAFS_ADMINS")
def update_degree_plans():
    try:
        with Session(engine) as session:
            #will need to add a for loop here for when there are multiple degree plans from agent output trying to be inserted
            existing_plan = (session.query(DegreePlan.DegreePlanMap).filter(DegreePlan.DegreePlanMap.degree == data["degree"]).first())

            if existing_plan:
                existing_plan.institution = data["institution"]
                existing_plan.majorcode = data["major_code"]
                existing_plan.credithourstotal = data["credit_hours_total"]
                existing_plan.notes = data["notes"]
                existing_plan.corecourses = data["core_courses"]
                existing_plan.concentrations = data["concentrations"]
                message = f"Updated existing degree plans"
            else:
                new_plan = DegreePlan.DegreePlanMap(
                    degree=data["degree"],
                    institution=data["institution"],
                    majorcode=data["major_code"],
                    credithourstotal=data["credit_hours_total"],
                    notes=data["notes"],
                    corecourses=data["core_courses"],
                    concentrations=data["concentrations"],
                )
                session.add(new_plan)
                message = f"Inserted new degree plan: {new_plan.degree}"

            session.commit()
            return jsonify({"message": message}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Failed to insert or update degree plan.", "error": str(e)}), 500