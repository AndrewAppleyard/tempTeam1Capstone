from flask import Flask, jsonify, request
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
import traceback
from datetime import datetime
from UserClasses import Advisor, User, Student, Admin

databaseURL = "mysql+pymysql://User:pass@localhost:3306/Test"
engine = create_engine(databaseURL)

if not database_exists(engine.url):
    create_database(engine.url)
    print("Database has been created!\n")
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base = User.Base.getBase()

base.metadata.create_all(bind=engine)

app = Flask(__name__)

@app.route("/Advisor/")
def getAdvisors():
    try:
        with Session(engine) as session:
            advisorData = Advisor.Advisor()
            advisorList = []
            
            results = session.execute(session.query(Advisor.AdvisorMap)).scalars()

            for advisor in results:
                a = Advisor.Advisor()
                a.userID = advisor.advisorID
                a.firstName = advisor.firstName
                a.lastName = advisor.lastName
                a.email = advisor.email
                a.phoneNumber = advisor.phoneNumber
                a.role = advisor.role
                a.school = advisor.school

                advisorList.append(a)

            return advisorList

    except Exception as e:
        traceback.print_exc()
        return "Failed to Execute Search"
    finally:
        session.close()

@app.route("/Advisor/<advisorID>", methods= ['GET', 'POST'] )
def getAdvisor(advisorID: int):
    try:
        with Session(engine) as session:
            result = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap == advisorID).first()
            
            advisor = Advisor.Advisor()

            advisor.advisorID = result.advisorID
            advisor.firstName = result.firstName
            advisor.lastName = result.lastName
            advisor.email = result.email
            advisor.phoneNumber = result.phoneNumber
            advisor.role = result.role
            advisor.school = result.school

            return advisor.__dict__
    except Exception as e:
        traceback.print_exc()
        return "Failed to Find Advisor"
    finally:
        session.close()

app.run(host="0.0.0.0", port=80)
