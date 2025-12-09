from datetime import datetime, timedelta
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

from UserClasses import Advisor, Student

path = os.path.abspath(__file__)
directory = os.path.dirname(path)

databaseURL = URL.decrypt(directory + "/config/config.txt", directory + "/config/.gitignore.key")

engine = create_engine(databaseURL)
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

dateFormatString = "%Y-%m-%d %H:%M:%S"

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
                a.advisortype = advisor.advisortype

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
            advisor.advisortype = result.advisortype

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
            s.phonenumber = student.phonenumber
            s.role = student.role
            s.school = student.school
            s.gpa = student.gpa
            s.major = student.major
            s.majorconcentration = student.majorconcentration
            s.minor = student.minor
            s.classstanding = student.classstanding
            s.registrationstatus = student.registrationstatus
            s.advisingstatus = student.advisingstatus
            s.activestatus = student.activestatus
            s.dateadvised = student.dateadvised
            s.financialhold = student.financialhold
            s.advisinghold = student.advisinghold
            s.academichold = student.academichold
            s.preferences = student.preferences
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
        try:
            studentid_int = int(studentid)
        except ValueError:
            return jsonify({"error": f"Invalid student ID format: {studentid}"}), 400
                
        with Session(engine) as session:
            statement = (
                select(Advisor.AdvisorMap)
                .join(Advisor.Advisor_And_StudentsMap, Advisor.AdvisorMap.advisorid == Advisor.Advisor_And_StudentsMap.advisorid)
                .filter(Advisor.Advisor_And_StudentsMap.studentid == studentid_int)
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
            advisor.advisortype = result.advisortype

            return jsonify(advisor.__dict__), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Failed to find advisor for student"}), 500

    finally:
        session.close()


@bp.route("/Appointment/Insert/<int:studentid>", methods=['POST'])
@role_required("UAFS_ADVISORS", "UAFS_STUDENTS")
def bookAppointment(studentid: int):

    advisorid = request.form.get('advisorid') 
    start_time_str = request.form.get('start_time')
    start_time = datetime.strptime(start_time_str, dateFormatString)

    with Session(engine) as session:
        new_appointment = Advisor.Appointment(
            advisorid = advisorid,
            studentid = studentid,
            starttime = start_time,
            endtime = start_time + timedelta(minutes=30),
            appointmentstatus = 'Scheduled'
        )
        session.add(new_appointment)
        session.commit()
        return "Appointment Scheduling Successful"
    
@bp.route("/Appointment/Cancel/<int:appointmentid>", methods=['POST'])
@role_required("UAFS_ADVISORS", "UAFS_STUDENTS") 
def cancelAppointment(appointmentid: int):
    try:
        with Session(engine) as session:
            statement = select(Advisor.Appointment).filter_by(appointmentid = appointmentid)
            appointmentrecord = session.scalars(statement).first()

            if not appointmentrecord:
                return jsonify({"error": f"Appointment with ID {appointmentid} not found."}), 404

            if appointmentrecord.appointmentstatus == 'Canceled':
                return jsonify({"message": f"Appointment ID {appointmentid} is already canceled."}), 200

            appointmentrecord.appointmentstatus = 'Canceled'
 
            session.commit()

            return jsonify({"message": f"Appointment ID {appointmentid} successfully canceled."}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": "An unexpected error occurred during cancellation."}), 500
    finally:
        session.close()

@bp.route("/Appointment/GetAppointmentByStudent/<int:studentid>", methods=['GET'])
@role_required("UAFS_ADVISORS", "UAFS_STUDENTS")
def getAppointmentByStudent(studentid: int):
    try:
        with Session(engine) as session:
            statement = (
                select(Advisor.Appointment)
                .filter_by(studentid=studentid)
                .filter(Advisor.Appointment.appointmentstatus != 'Canceled')
                .order_by(Advisor.Appointment.starttime.desc())
            )
            appointment_record = session.scalars(statement).first()

            if not appointment_record:
                return jsonify({"error": f"Scheduled appointment for Student ID {studentid} not found."}), 404

            appointment_data = {
                "appointmentid": appointment_record.appointmentid,
                "advisorid": appointment_record.advisorid,
                "studentid": appointment_record.studentid,
                "starttime": appointment_record.starttime.strftime(dateFormatString),
                "endtime": appointment_record.endtime.strftime(dateFormatString),
                "appointmentstatus": appointment_record.appointmentstatus
            }

            return jsonify(appointment_data), 200

    except Exception as e:
        print(f"Error retrieving appointment by student ID: {e}") 
        return jsonify({"error": "Error fetching appointment."}), 500
    finally:
        session.close()

@bp.route("/Appointment/GetAdvisorAppointments/<int:advisorid>", methods=['GET'])
@role_required("UAFS_ADVISORS", "UAFS_STUDENTS")
def getAdvisorAppointments(advisorid: int):
    try:
        with Session(engine) as session:
            statement = (
                select(Advisor.Appointment)
                .filter_by(advisorid=advisorid)
                .filter(Advisor.Appointment.appointmentstatus != 'Canceled')
                .filter(Advisor.Appointment.starttime >= datetime.now())
            )
            
            appointment_records = session.scalars(statement).all()

            if not appointment_records:
                return jsonify({"message": f"No active appointments found for Advisor ID {advisorid}."}), 200

            all_appointments_data = []
            for record in appointment_records:
                appointment_data = {
                    "appointmentid": record.appointmentid,
                    "advisorid": record.advisorid,
                    "studentid": record.studentid,
                    "starttime": record.starttime.strftime(dateFormatString),
                    "endtime": record.endtime.strftime(dateFormatString),
                    "appointmentstatus": record.appointmentstatus
                }
                all_appointments_data.append(appointment_data)

            return jsonify(all_appointments_data), 200

    except Exception as e:
        print(f"Error retrieving advisor appointments: {e}") 
        return jsonify({"error": "Error fetching advisor appointments."}), 500
    finally:
        session.close()

@bp.route("/Appointment/Next/<int:advisorid>", methods=['GET'])
@role_required("UAFS_ADVISORS", "UAFS_ADMINS")
def getNextAppointment(advisorid: int):
    try:
        with Session(engine) as session:
            statement = (
                select(Advisor.Appointment)
                .filter_by(advisorid=advisorid)
                .filter(Advisor.Appointment.appointmentstatus != 'Canceled')
                .filter(Advisor.Appointment.starttime >= datetime.now())
                .order_by(Advisor.Appointment.starttime.asc())
            )
            appt = session.scalars(statement).first()
            if not appt:
                return jsonify({"message": "No upcoming appointments"}), 200

            start_local = appt.starttime.replace(tzinfo=None) if appt.starttime.tzinfo else appt.starttime
            end_local = appt.endtime.replace(tzinfo=None) if appt.endtime and appt.endtime.tzinfo else appt.endtime
            data = {
                "appointmentid": appt.appointmentid,
                "advisorid": appt.advisorid,
                "studentid": appt.studentid,
                "starttime": start_local.isoformat() if start_local else None,
                "endtime": end_local.isoformat() if end_local else None,
                "appointmentstatus": appt.appointmentstatus
            }
            return jsonify(data), 200
    except Exception as e:
        print(f"Error retrieving next appointment: {e}")
        return jsonify({"error": "Error fetching next appointment."}), 500
    finally:
        session.close()

@bp.route("/Appointment/AvailableSlots/<int:advisorid>", methods=['GET'])
@role_required("UAFS_ADVISORS", "UAFS_STUDENTS")
def getAvailableSlots(advisorid: int):
    try:
        date_str = request.args.get("date")
        if not date_str:
            return jsonify({"error": "Missing date parameter"}), 400
        
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        if selected_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return jsonify([]), 200

        start_of_day = datetime.combine(selected_date, datetime.strptime("09:00", "%H:%M").time())
        end_of_day = datetime.combine(selected_date, datetime.strptime("17:00", "%H:%M").time())

        all_slots = []
        current = start_of_day
        while current < end_of_day:
            all_slots.append(current)
            current += timedelta(minutes=30)

        with Session(engine) as session:
            statement = (
                select(Advisor.Appointment)
                .filter_by(advisorid=advisorid)
                .filter(Advisor.Appointment.appointmentstatus != 'Canceled')
                .filter(Advisor.Appointment.starttime >= start_of_day)
                .filter(Advisor.Appointment.starttime < end_of_day)
            )
            booked = session.scalars(statement).all()

        booked_times = {appt.starttime for appt in booked}

        available_slots = []
        now = datetime.now()

        for slot in all_slots:
            if slot in booked_times:
                continue
            if selected_date == now.date() and slot <= now:
                continue

            available_slots.append(slot.strftime("%H:%M"))

        return jsonify(available_slots), 200

    except Exception as e:
        print("Error in getAvailableSlots:", e)
        return jsonify({"error": "Error generating available time slots"}), 500
