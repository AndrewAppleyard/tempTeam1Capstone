from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import traceback
from datetime import datetime
import os, sys, json, re
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from functools import wraps
from Advising.APIs import URL
from UserClasses.Student import StudentMap
from UserClasses.DegreePlan import DegreePlanMap
from UserClasses.CurrentCourse import CurrentCourseMap
from UserClasses.Transcript import TranscriptMap
from UserClasses import Student, User

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
Always generate schedules that satisfy ALL constraints and preferences provided below.

STUDENT DATA
- Use the student's transcript to determine completed courses.
- Never recommend a class already completed.
- Consider the student's year and progression level.
- Maintain reasonable difficulty balance:
    * Juniors/Seniors: 1000-4000 level 
    * Freshman/Sophomores: mostly 1000-2000 level
- If a high-level course is required, include it even if difficult.

DEGREE PLAN DATA
- Use corecourses dict as a guide to remaining requirements.
- Use concentrations dict if student has declared one.
- Use notes for elective rules and upper-level requirements.
- Do NOT mirror the exact semester plan; pick ANY remaining requirements/electives offered this term if prereqs are satisfied.
- Respect prerequisite sequencing, but you may pull courses from earlier/later terms if available.

CURRENT COURSE OFFERINGS
- Only choose from the CURRENT semester's offerings provided to you.
- DO NOT invent courses or section numbers.
- Make sure meeting patterns do not conflict.

PREFERENCES (soft guidance)
- Consider student.preferences if provided; they are preferences, not hard rules.
- Try to align with preferredDays, timeOfDay, modality, avoidBackToBack when possible.
- preferredCreditHours is most important; if > 15, strongly aim to meet it (often for scholarships).
- Earliest/Latest times should be respected when feasible, but may be relaxed if needed.

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

time_pattern = re.compile(r'(\d{1,2}:\d{2})\s*(AM|PM)', flags=re.IGNORECASE)


def _extract_days(day_part: str):
    normalized = re.sub(r'[^A-Za-z]', '', day_part).upper()
    if normalized.startswith("MEETING"):
        normalized = normalized[len("MEETING"):]
    days = []
    i = 0
    while i < len(normalized):
        if normalized.startswith("TH", i):
            days.append("TH")
            i += 2
            continue
        if normalized.startswith("TU", i):
            days.append("T")
            i += 2
            continue
        char = normalized[i]
        if char in {"M", "T", "W", "R", "F"}:
            days.append(char)
        elif char == "H":  # Sometimes used for Thursday
            days.append("TH")
        i += 1
    return days


def _to_minutes(time_text, meridian):
    try:
        dt = datetime.strptime(f"{time_text} {meridian.upper()}", "%I:%M %p")
        return dt.hour * 60 + dt.minute
    except Exception:
        return None


def parse_meeting_blocks(meeting_pattern: str):
    """
    Convert a meeting pattern into comparable time blocks for conflict detection.
    Returns a list of dicts: {"day": str, "start": minutes, "end": minutes}
    """
    if not meeting_pattern or not isinstance(meeting_pattern, str):
        return []

    upper = meeting_pattern.upper()
    if any(keyword in upper for keyword in ("ONLINE", "TBA", "ASYNC")):
        return []

    matches = list(time_pattern.finditer(meeting_pattern))
    if len(matches) < 2:
        return []

    start_match, end_match = matches[0], matches[1]
    start_minutes = _to_minutes(start_match.group(1), start_match.group(2))
    end_minutes = _to_minutes(end_match.group(1), end_match.group(2))
    if start_minutes is None or end_minutes is None or end_minutes <= start_minutes:
        return []

    day_part = meeting_pattern[: start_match.start()].strip()
    days = _extract_days(day_part)
    if not days:
        return []

    return [{"day": day, "start": start_minutes, "end": end_minutes} for day in days]


def _base_course_key(code: str):
    if not code:
        return ""
    cleaned = str(code).strip()
    match = re.match(r"^(.*?)-\d{3,}$", cleaned)
    base = match.group(1) if match else cleaned
    return base.lower()


def resolve_conflicts_with_replacements(courses, offerings):
    day_schedule = {}
    used_offering_codes = set()
    filtered = []

    offerings_by_base = {}
    for offer in offerings or []:
        if not isinstance(offer, dict):
            continue
        status = (offer.get("status") or "").lower()
        if status and status != "open":
            continue
        base_key = _base_course_key(offer.get("code"))
        offerings_by_base.setdefault(base_key, []).append(offer)

    for course in courses:
        if not isinstance(course, dict):
            continue

        pattern = course.get("meeting_pattern") or course.get("meetingpattern") or ""
        blocks = parse_meeting_blocks(pattern)

        conflict = False
        for block in blocks:
            for existing in day_schedule.get(block["day"], []):
                if block["start"] < existing["end"] and existing["start"] < block["end"]:
                    conflict = True
                    break
            if conflict:
                break

        if not conflict:
            filtered.append(course)
            for block in blocks:
                day_schedule.setdefault(block["day"], []).append(block)
            course_code = course.get("code")
            if course_code:
                used_offering_codes.add(course_code)
            continue

        base_key = _base_course_key(course.get("code"))
        alternatives = offerings_by_base.get(base_key, [])
        replacement = None

        for alt in alternatives:
            alt_code = alt.get("code")
            if alt_code in used_offering_codes:
                continue
            alt_pattern = alt.get("meeting_pattern") or ""
            alt_blocks = parse_meeting_blocks(alt_pattern)
            conflict_alt = False
            for block in alt_blocks:
                for existing in day_schedule.get(block["day"], []):
                    if block["start"] < existing["end"] and existing["start"] < block["end"]:
                        conflict_alt = True
                        break
                if conflict_alt:
                    break
            if conflict_alt:
                continue

            replacement = {
                **course,
                "code": alt.get("code", course.get("code")),
                "title": alt.get("title", course.get("title")),
                "delivery_mode": alt.get("delivery_mode", course.get("delivery_mode")),
                "meeting_pattern": alt_pattern or course.get("meeting_pattern"),
                "location": alt.get("location", course.get("location")),
                "instructor": alt.get("instructor", course.get("instructor")),
                "status": alt.get("status", course.get("status"))
            }
            used_offering_codes.add(alt_code)
            for block in alt_blocks:
                day_schedule.setdefault(block["day"], []).append(block)
            filtered.append(replacement)
            break

        # If no replacement found, drop the conflicting course (do not append).

    return filtered

def generate_schedule_with_agent(student, transcript, degreeplan, current_courses, target_semester):
    system_prompt = systemprompt.replace("{target_semester}", target_semester)

    user_content = {
        "student": {
            "name": f"{student.firstname} {student.lastname}",
            "student_id": student.studentid,
            "major": student.major,
            "transcript": transcript.coursemap if transcript else [],
            "preferences": student.preferences if getattr(student, "preferences", None) else {}
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
        max_tokens=1000,
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

            if isinstance(schedule, dict) and "courses" in schedule:
                filtered_courses = resolve_conflicts_with_replacements(schedule.get("courses", []), current_course_list)
                schedule["courses"] = filtered_courses
                student.classes = filtered_courses
            elif isinstance(schedule, list):
                filtered_courses = resolve_conflicts_with_replacements(schedule, current_course_list)
                schedule = filtered_courses
                student.classes = filtered_courses
            else:
                student.classes = schedule

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
- Student level (e.g., Freshman/Sophomore/Junior/Senior) is provided in the "year" field of the transcript object.

RULES:
- The students classes field is not empty.
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
    transcript_payload = None
    if transcript:
        transcript_payload = {
            "coursemap": transcript.coursemap,
            "year": transcript.year,
            "program": transcript.program,
            "concentration": transcript.concentration
        }

    user_content = {
        "student": {
            "id": student.studentid,
            "name": f"{student.firstname} {student.lastname}",
            "major": student.major,
            "gpa": student.gpa,
            "classstanding": student.classstanding,
            "financial_hold": student.financialhold,
            "academic_hold": student.academichold,
            "advising_hold": student.advisinghold,
            "advising_status": student.advisingstatus,
            "registration_status": student.registrationstatus,
            "classes": student.classes
        },
        "transcript": transcript_payload
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
