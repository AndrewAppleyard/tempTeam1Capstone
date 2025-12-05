import traceback
from UserClasses import Transcript
from cryptography.fernet import Fernet
import os, sys
from flask import Flask, jsonify, request, Blueprint
from sqlalchemy import Column, Integer, String, create_engine, select, text
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
from selenium.common.exceptions import TimeoutException
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from functools import wraps
from Advising.APIs import URL

bp = Blueprint('TranscriptAPI', __name__, url_prefix='/Transcript')

path = os.path.abspath(__file__)
directory = os.path.dirname(path)

databaseURL = URL.decrypt(directory + "/config/config.txt", directory + "/config/.gitignore.key")

engine = create_engine(databaseURL)
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = Flask(__name__)

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


@bp.route("/Student/GetTranscripts/<int:studentid>", methods=['GET'])
@role_required("UAFS_STUDENTS", "UAFS_ADVISORS", "UAFS_ADMINS")
def getTranscriptsByStudentId(studentid: int):
    try:
        with Session(engine) as session:
            results = session.query(Transcript.TranscriptMap) \
                             .filter(Transcript.TranscriptMap.studentid == studentid) \
                             .all()
            
            if not results:
                return jsonify([]), 200 

            transcript_list = []
            
            for transcript in results:
                transcript_info = {
                    "transcriptid": transcript.transcriptid,
                    "studentid": transcript.studentid,
                    "program": transcript.program,
                    "concentration": transcript.concentration,
                    "year": transcript.year,
                    "institution": transcript.institution,
                    "coursemap": transcript.coursemap,
                    "cumulativegpa": transcript.cumulativegpa,
                }
                transcript_list.append(transcript_info)
            
            return jsonify(transcript_list), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Failed to retrieve transcripts"}), 500
    finally:
        session.close()

@bp.route("/Student/AddTranscript/<int:id>", methods=['GET','POST'])
@role_required("UAFS_STUDENTS", "UAFS_ADVISORS")
def addTranscript() -> None:
    transcript = Transcript.TranscriptMap()
    transcript.studentid = request.form.get('studentid')
    transcript.program = request.form.get('program')
    transcript.concentration = request.form.get('concentration')
    transcript.year = request.form.get('year')
    transcript.institution = request.form.get('institution')
    transcript.coursemap = request.form.get('coursemap')
    transcript.cumulativegpa = request.form.get('cumulativegpa')
    
    try:
        with Session(engine) as session:
            session.add(transcript)
            session.commit()
            session.refresh(transcript)

            return f"Transcript added for student id {request.form.get('studentid')}"
    except Exception as e:
        traceback.print_exc()
        session.rollback()

        return "Transcript Add Failed"
    finally:
        session.close()

@bp.route("/Student/UpdateTranscript/<int:id>", methods=['GET','POST'])
@role_required("UAFS_STUDENTS", "UAFS_ADVISORS")
def updateTranscript() -> None:
    try:
        with Session(engine) as session:
            transcript = session.query(Transcript.TranscriptMap).filter(Transcript.TranscriptMap.transcriptid == id).first() #studentid == id?
            if(request.form.get('program') != None):
                transcript.program = request.form.get('program')
            if(request.form.get('subject') != None):
                transcript.subject = request.form.get('subject')
            if(request.form.get('concentration') != None):
                transcript.concentration = request.form.get('concentration')
            if(request.form.get('year') != None):
                transcript.year = request.form.get('year')
            if(request.form.get('institution') != None):
                transcript.institution = request.form.get('institution')
            if(request.form.get('cumulativegpa') != None):
                transcript.cumulativegpa = request.form.get('cumulativegpa')
            if(request.form.get('coursemap') != None):
                transcript.coursemap = request.form.get('coursemap')

            session.commit()

            return f"Transcript updated for student id {request.form.get('studentid')}"
    except Exception as e:
        traceback.print_exc()
        session.rollback()

        return "Transcript Update Failed"
    finally:
        session.close()
