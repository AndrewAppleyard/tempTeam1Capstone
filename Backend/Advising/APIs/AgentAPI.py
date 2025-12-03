from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import traceback
from datetime import datetime
import os, sys, json
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from functools import wraps
from Advising.APIs import URL
from UserClasses.Student import StudentMap
from UserClasses.DegreePlan import DegreePlanMap
from UserClasses.CurrentCourse import CurrentCourseMap
from UserClasses.Transcript import TranscriptMap

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

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

systemprompt = """
You are UAFS-Schedule-Gen, an automated degree-progress-aware scheduling agent. 
You generate the student's next semester schedule using ONLY the data provided.

STUDENT DATA
- Use the student's transcript to determine completed courses.
- Never recommend a class already completed.
- Consider the student's year and progression level.
- Maintain reasonable difficulty balance:
    * Juniors/Seniors: mostly 3000-4000 level 
    * Freshman/Sophomores: mostly 1000-2000 level
- If a high-level course is required, include it even if difficult.

DEGREE PLAN DATA
- Use corecourses dict to know semester ordering.
- Use concentrations dict if student has declared one.
- Use notes for elective rules and upper-level requirements.
- Follow prerequisite ordering implied by degree plan's semester sequence.

CURRENT COURSE OFFERINGS
- Only choose from the CURRENT semester's offerings provided to you.
- DO NOT invent courses or section numbers.
- Make sure meeting patterns do not conflict.
- Only include open sections ("Status": "Open").

SEMESTER RULES
- Target semester is always: {target_semester}
- Choose 12-18 credits unless the degree plan requires otherwise.
- If a required course is NOT available this term, skip it.


OUTPUT FORMAT (JSON ONLY)
{
"semester": "{target_semester}",
"courses": [
    {
    "code": "",
    "title": "",
    "credits": 0,
    "delivery_mode": "",
    "meeting_pattern": "",
    "location": "",
    "instructor": ""
    }
]
}

ONLY output valid JSON. No explanations, no markdown.
If data is missing, return an empty schedule list instead of hallucinating.
"""

def generate_schedule_with_agent(student, transcript, degreeplan, current_courses, target_semester):
    system_prompt = systemprompt.replace("{target_semester}", target_semester)

    user_content = {
        "student": {
            "name": f"{student.firstname} {student.lastname}",
            "student_id": student.studentid,
            "major": student.major,
            "transcript": transcript.coursemap
        },
        "degree_plan": {
            "degree": degreeplan.degree,
            "major_code": degreeplan.majorcode,
            "corecourses": degreeplan.corecourses,
            "concentrations": degreeplan.concentrations,
            "notes": degreeplan.notes
        },
        "current_courses": current_courses
    }

    completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_format={"type": "json_object"},
        max_tokens=600,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_content)}
        ]
    )

    return json.loads(completion.choices[0].message.content)

@bp.route("/GenerateSchedule/<int:student_id>", methods=["POST"])
@role_required("UAFS_STUDENTS", "UAFS_ADMINS")
def generate_schedule(student_id):
    try:    

        target_semester = "Spring 2026"

        with Session(engine) as session:
            student = session.query(StudentMap).filter(StudentMap.studentid == student_id).first()

            if not student:
                return jsonify({"message": "Student not found"}), 404

            if not student.major:
                return jsonify({"message": "Student missing major"}), 400

            degreeplan = session.query(DegreePlanMap).filter(DegreePlanMap.degree == student.major).first()

            if not degreeplan:
                return jsonify({"message": f"No degree plan found for {student.major}"}), 404


            transcript = session.query(TranscriptMap).filter(TranscriptMap.studentid == student_id).first()


            current_courses = session.query(CurrentCourseMap).filter(CurrentCourseMap.academicperiod.contains(target_semester)).all()

            current_course_list = []

            for c in current_courses:
                if " - " in c.section:
                    code, title = c.section.split(" - ", 1)
                else:
                    code = c.section
                    title = c.section

                current_course_list.append({
                    "code": code,
                    "title": title,
                    "status": c.courseavailability,
                    "delivery_mode": c.deliverymode,
                    "meeting_pattern": c.meetingpattern,
                    "location": c.courselocation,
                    "instructor": c.instructor,
                    "capacity": c.capacity,
                    "enrolled": c.enrolled,
                    "academic_period": c.academicperiod,
                    "startdate": c.startdate
                })

            schedule = generate_schedule_with_agent(student, transcript, degreeplan, current_course_list, target_semester)

            if "courses" in schedule:
                student.classes = schedule["courses"]

            session.commit()

            return jsonify({
                "message": "Schedule generated successfully",
                "schedule": schedule
            }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Failed to generate schedule.", "error": str(e)}), 500

advising_hold_prompt = """
You are UAFS-Advising-Agent, an automated evaluator that determines 
whether a student's advising hold should be lifted.

You will receive structured JSON containing:
- GPA
- Completed courses (transcript)
- Degree progress
- Holds (financial, academic)
- Advising status
- Registration status
- Major & concentration

RULES:
- Only lift the advising hold if the student is in good standing.
- DO NOT lift the hold if there is:
    * An academic hold
    * A financial hold
    * Missing required advising steps
    * No transcript or incomplete academic data
- If a student is a Freshman or Sophomore or are new to the degree (for example they just switched majors) it is very recommended for them to have to meet with an advisor.
- If the student is fully advised AND has no other holds, recommend lifting the advising hold.

OUTPUT (JSON ONLY):
{
  "lift_advising_hold": true/false,
  "reason": "short explanation"
}

No markdown. No additional text.
"""

def check_advising_hold_with_agent(student, transcript):
    user_content = {
        "student": {
            "id": student.studentid,
            "name": f"{student.firstname} {student.lastname}",
            "major": student.major,
            "gpa": student.gpa,
            "financial_hold": student.financialhold,
            "academic_hold": student.academichold,
            "advising_hold": student.advisinghold,
            "advising_status": student.advisingstatus,
            "registration_status": student.registrationstatus,
        },
        "transcript": transcript.coursemap
    }

    completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_format={"type": "json_object"},
        max_tokens=300,
        messages=[
            {"role": "system", "content": advising_hold_prompt},
            {"role": "user", "content": json.dumps(user_content)}
        ]
    )

    return json.loads(completion.choices[0].message.content)

@bp.route("/CheckAdvisingHold/<int:student_id>", methods=["POST"])
@role_required("UAFS_STUDENTS", "UAFS_ADMINS")
def check_advising_hold(student_id):
    try:
        with Session(engine) as session:

            student = session.query(StudentMap).filter(StudentMap.studentid == student_id).first()
            if not student:
                return jsonify({"message": "Student not found"}), 404

            transcript = session.query(TranscriptMap).filter(TranscriptMap.studentid == student_id).first()

            result = check_advising_hold_with_agent(student, transcript)

            if result.get("lift_advising_hold") is True:
                student.advisinghold = False
                student.advisingstatus = True
                student.registrationstatus = True

                student.dateadvised = datetime.now()
                session.commit()

            return jsonify({
                "message": "Advising hold agent check complete",
                "result": result
            }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Failed to check advising hold.", "error": str(e)}), 500