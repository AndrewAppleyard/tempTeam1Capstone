from flask import Blueprint, Flask, jsonify, request
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
import traceback
from datetime import datetime, timedelta, timezone
import os, sys, smtplib
from ldap3 import Server, Connection, ALL
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from functools import wraps
from Advising.APIs import URL


bp = Blueprint('StudentAPI', __name__, url_prefix="/Student")

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)

from UserClasses import Advisor, User, Student, Admin, Transcript
from UserClasses.Advisor import Appointment

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


def _send_sms(to_number: str, body: str):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")

    if not (account_sid and auth_token and from_number):
        print("SMS skipped: Twilio env vars not configured.")
        return False

    digits = "".join(ch for ch in str(to_number or "") if ch.isdigit())
    if not digits:
        return False
    if len(digits) == 10:
        to_e164 = f"+1{digits}"
    elif len(digits) == 11 and digits.startswith("1"):
        to_e164 = f"+{digits}"
    elif digits.startswith("+"):
        to_e164 = digits
    else:
        to_e164 = f"+{digits}"

    try:
        import requests
    except ImportError:
        print("SMS skipped: requests not available.")
        return False

    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        data = {
            "From": from_number,
            "To": to_e164,
            "Body": body
        }
        resp = requests.post(url, data=data, auth=(account_sid, auth_token))
        if 200 <= resp.status_code < 300:
            return True
        print(f"Twilio SMS failed: {resp.status_code} {resp.text}")
        return False
    except Exception as e:
        print("SMS send exception:", e)
        return False


def _format_phone(raw):
    s = str(raw or "").strip()
    if not s:
        return None
    if s.startswith("+"):
        return s
    digits = "".join(ch for ch in s if ch.isdigit())
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return f"+{digits}" if digits else None

@bp.route("/", methods=['GET'])
@role_required("UAFS_ADMINS")
def getStudents():
    '''token = get_jwt()
    if token["Role"] == "Student":
        print("Access succesful!")
    else:
        print("Can't access with current role.")
        return jsonify({"message":"Can't access with current role."}), 401'''
    
    try:
        with Session(engine) as session:
            students = session.query(Student.StudentMap).all()
            result = []

            for s in students:
                transcript = (session.query(Transcript.TranscriptMap).filter(Transcript.TranscriptMap.studentid == s.studentid).first())

                transcript_json = None
                if transcript:
                    transcript_json = {
                        "transcriptid": transcript.transcriptid,
                        "studentid": transcript.studentid,
                        "program": transcript.program,
                        "concentration": transcript.concentration,
                        "year": transcript.year,
                        "institution": transcript.institution,
                        "coursemap": transcript.coursemap,
                        "cumulativegpa": transcript.cumulativegpa
                    }

                result.append({
                    "studentid": s.studentid,
                    "firstname": s.firstname,
                    "lastname": s.lastname,
                    "email": s.email,
                    "phonenumber": s.phonenumber,
                    "role": s.role,
                    "school": s.school,
                    "gpa": s.gpa,
                    "major": s.major,
                    "majorconcentration": s.majorconcentration,
                    "minor": s.minor,
                    "classstanding": s.classstanding,
                    "registrationstatus": s.registrationstatus,
                    "advisingstatus": s.advisingstatus,
                    "activestatus": s.activestatus,
                    "dateadvised": s.dateadvised,
                    "financialhold": s.financialhold,
                    "advisinghold": s.advisinghold,
                    "academichold": s.academichold,
                    "preferences": s.preferences,
                    "classes": s.classes,
                    "transcript": transcript_json
                })

            return jsonify(result)
        
    except Exception as e:
        
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()


def send_sms_reminders(session: Session, now: datetime):
    window_24h_start = now + timedelta(hours=23)
    window_24h_end = now + timedelta(hours=25)
    window_3h_start = now + timedelta(hours=2)
    window_3h_end = now + timedelta(hours=4)

    base_query = (
        session.query(Appointment, Student.StudentMap)
        .join(Student.StudentMap, Appointment.studentid == Student.StudentMap.studentid)
        .filter(Appointment.appointmentstatus == "Scheduled")
    )

    reminders_sent = {"24h": 0, "3h": 0}

    appts_24h = base_query.filter(
        Appointment.starttime >= window_24h_start,
        Appointment.starttime <= window_24h_end,
        Appointment.reminded_24h == False  # noqa: E712
    ).all()

    for appt, stu in appts_24h:
        to = _format_phone(stu.phonenumber)
        if not to:
            continue
        start_local = appt.starttime
        body = f"Reminder: Advising appointment on {start_local.strftime('%a %b %d at %I:%M %p')}."
        if _send_sms(to, body):
            appt.reminded_24h = True
            reminders_sent["24h"] += 1

    appts_3h = base_query.filter(
        Appointment.starttime >= window_3h_start,
        Appointment.starttime <= window_3h_end,
        Appointment.reminded_3h == False  # noqa: E712
    ).all()

    for appt, stu in appts_3h:
        to = _format_phone(stu.phonenumber)
        if not to:
            continue
        start_local = appt.starttime
        body = f"Reminder: Advising appointment today at {start_local.strftime('%I:%M %p')}."
        if _send_sms(to, body):
            appt.reminded_3h = True
            reminders_sent["3h"] += 1

    session.commit()
    return reminders_sent


@bp.route("/<int:studentid>",methods = ['GET', 'POST'])
@role_required("UAFS_STUDENTS", "UAFS_ADVISORS", "UAFS_ADMINS")
def getStudentInfo(studentid: int):

    try:
        with Session(engine) as session:
            student = session.query(Student.StudentMap).filter(Student.StudentMap.studentid == studentid).first()
            if not student:
                return jsonify({"error": "Student not found"}), 404

            student_result = {}
            student_result["studentid"] = student.studentid
            student_result["firstname"] = student.firstname
            student_result["lastname"] = student.lastname
            student_result["email"] = student.email
            student_result["phonenumber"] = student.phonenumber
            student_result["role"] = student.role
            student_result["school"] = student.school
            student_result["gpa"] = student.gpa
            student_result["major"] = student.major
            student_result["majorconcentration"] = student.majorconcentration
            student_result["minor"] = student.minor
            student_result["classstanding"] = student.classstanding
            student_result["registrationstatus"] = student.registrationstatus
            student_result["advisingstatus"] = student.advisingstatus
            student_result["activestatus"] = student.activestatus #actvestatus added
            student_result["dateadvised"] = student.dateadvised
            student_result["financialhold"] = student.financialhold
            student_result["advisinghold"] = student.advisinghold
            student_result["academichold"] = student.academichold
            student_result["preferences"] = student.preferences
            student_result["classes"] = student.classes


            transcript = session.query(Transcript.TranscriptMap).filter(Transcript.TranscriptMap.studentid == studentid).first()

            if transcript:
                transcript_result = {}
                transcript_result["transcriptid"] = transcript.transcriptid
                transcript_result["studentid"] = transcript.studentid
                transcript_result["program"] = transcript.program
                transcript_result["concentration"] = transcript.concentration
                transcript_result["year"] = transcript.year
                transcript_result["institution"] = transcript.institution
                transcript_result["coursemap"] = transcript.coursemap
                transcript_result["cumulativegpa"] = transcript.cumulativegpa
            else:
                transcript_result = None

            return jsonify({
                "student": student_result,
                "transcript": transcript_result
            }), 200


    except Exception as e:
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()


@bp.route("/SendSMSReminders", methods=['POST'])
@role_required("UAFS_ADMINS")
def trigger_sms_reminders():
  now = datetime.now(timezone.utc)
  try:
    with Session(engine) as session:
      sent = send_sms_reminders(session, now)
      return jsonify({"message": "Reminder job completed", "sent": sent}), 200
  except Exception as e:
    traceback.print_exc()
    return jsonify({"message": "Failed to send SMS reminders.", "error": str(e)}), 500


@bp.route("/TestSMS/<int:studentid>", methods=['POST'])
@role_required("UAFS_STUDENTS", "UAFS_ADVISORS", "UAFS_ADMINS")
def send_test_sms(studentid: int):
    try:
        with Session(engine) as session:
            student = session.query(Student.StudentMap).filter(Student.StudentMap.studentid == studentid).first()
            if not student:
                return jsonify({"message": "Student not found"}), 404

            advisor = None
            # try to find advisor via linking table
            link = session.query(Advisor.Advisor_And_StudentsMap).filter(Advisor.Advisor_And_StudentsMap.studentid == studentid).first()
            if link:
                advisor = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap.advisorid == link.advisorid).first()

            to = _format_phone(student.phonenumber)
            if not to:
                return jsonify({"message": "No valid phone number for student."}), 400

            advisor_name = advisor.firstname + " " + advisor.lastname if advisor else "your advisor"
            body = f"Advising reminder: Hi {student.firstname or 'student'}, you have 3 hours until your advising appointment with {advisor_name}."
            if _send_sms(to, body):
                return jsonify({"message": "Test SMS sent."}), 200
            return jsonify({"message": "Failed to send SMS."}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Failed to send SMS.", "error": str(e)}), 500

@bp.route("/Update/<int:id>", methods = ['GET','POST'])
@role_required("UAFS_ADMINS", "UAFS_STUDENTS", "UAFS_ADVISORS")
def updateStudent(id: int) -> None:
    token = get_jwt()
    try:
        with Session(engine) as session:
            false = "false"
            true = "true"
            student = session.query(Student.StudentMap).filter(Student.StudentMap.studentid == id).first()

            preferences_payload = None
            classes_payload = None
            if request.form.get('preferences') is not None:
                try:
                    raw_preferences = request.form.get('preferences')
                    preferences_payload = json.loads(raw_preferences) if raw_preferences else {}
                except json.JSONDecodeError:
                    return jsonify({"message": "Invalid preferences payload"}), 400
            
            if request.form.get('classes') is not None:
                try:
                    raw_classes = request.form.get('classes')
                    classes_payload = json.loads(raw_classes) if raw_classes else []
                except json.JSONDecodeError:
                    return jsonify({"message": "Invalid classes payload"}), 400

            if (token["Role"] == 'UAFS_STUDENTS'):
                if(request.form.get('phonenumber') != None):
                    student.phonenumber = request.form.get('phonenumber')
                if preferences_payload is not None:
                    student.preferences = preferences_payload
                if classes_payload is not None:
                    student.classes = classes_payload
                    
            elif (token["Role"] == 'UAFS_ADVISORS'):
                if(request.form.get('major') != None):
                    student.major = request.form.get('major')
                if(request.form.get('majorconcentration') != None):
                    student.majorconcentration = request.form.get('majorconcentration')
                if(request.form.get('minor') != None):
                    student.minor = request.form.get('minor')
                if(request.form.get('classstanding') != None):
                    student.classstanding = request.form.get('classstanding')
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
                if preferences_payload is not None:
                    student.preferences = preferences_payload
                if classes_payload is not None:
                    student.classes = classes_payload

            elif (token["Role"] == 'UAFS_ADMINS'):
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
                if(request.form.get('gpa') != None):
                    student.school = request.form.get('gpa')
                if(request.form.get('major') != None):
                    student.major = request.form.get('major')
                if(request.form.get('majorconcentration') != None):
                    student.majorconcentration = request.form.get('majorconcentration')
                if(request.form.get('minor') != None):
                    student.minor = request.form.get('minor')
                if(request.form.get('classstanding') != None):
                    student.classstanding = request.form.get('classstanding')
                if(request.form.get('dateadvised') != None):
                    date = datetime.strptime(request.form.get('dateadvised'), dateFormatString)
                    student.dateadvised = date
                if(request.form.get('registrationstatus') != None):
                    if(request.form.get('registrationstatus').casefold() == true.casefold()):
                        student.registrationstatus = True
                    elif(request.form.get('registrationstatus').casefold() == false.casefold()):
                        student.registrationstatus = False
                if(request.form.get('advisingstatus') != None):
                    if(request.form.get('advisingstatus').casefold() == true.casefold()):
                        student.advisingstatus = True
                    elif(request.form.get('advisingstatus').casefold() == false.casefold()):
                        student.advisingstatus = False
                if(request.form.get('activestatus') != None):
                    if(request.form.get('activestatus').casefold() == true.casefold()):
                        student.activestatus = True
                    elif(request.form.get('activestatus').casefold() == false.casefold()):
                        student.activestatus = False
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
                if preferences_payload is not None:
                    student.preferences = preferences_payload
                if classes_payload is not None:
                    student.classes = classes_payload
            
            session.commit()

            return "Student Update Successful"
    except Exception as e:
        traceback.print_exc()
        session.rollback()
        return {"error": "Update failed"}, 400
    finally:
        session.close()