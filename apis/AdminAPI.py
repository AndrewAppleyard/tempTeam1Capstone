from flask import Flask, jsonify, request
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase, Session
from sqlalchemy_utils import database_exists, create_database
from pymysql import install_as_MySQLdb
import json
import traceback
from UserClasses import Advisor, User

databaseURL = "mysql+pymysql://User:pass@localhost:3306/Test"
engine = create_engine(databaseURL)

if not database_exists(engine.url):
    create_database(engine.url)
    print("Database has been created!\n")
    
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


base = User.Base.getBase()

class AdvisorMap(Base):
    __tablename__="Advisor"

    advisorID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstName: Mapped[str] = mapped_column(String(255))
    lastName: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))

base.metadata.create_all(bind=engine)

app = Flask(__name__)


@app.route("/")
def test():
    return "This is a test"

@app.route("/Advisor/<firstName>/<lastName>/<email>")
def addAdvisor(firstName: str, lastName: str, email: str) -> None:
    advisor = Advisor()
    advisor.firstName = firstName
    advisor.lastName = lastName
    advisor.email = email

    try:
        with Session(engine) as session:
            session.add(advisor)
            session.commit()
            session.refresh(advisor)
            session.close()
    except:
        print("Failed to add Advisor")
    finally:
        pass
        

@app.route("/Advisor/firstName/<firstName>/lastName/<lastName>")
def getAdvisor(firstName: str, lastName: str):
   
    try:
        with Session(engine) as session:
            result = session.query(Advisor.AdvisorMap).filter(Advisor.AdvisorMap.firstName == firstName).filter(Advisor.AdvisorMap.lastName == lastName).first()
            session.close()

            advisor = Advisor.Advisor()

            advisor.advisorID = result.advisorID
            advisor.firstName = result.firstName
            advisor.lastName = result.lastName
            advisor.email = result.email

            return advisor.__dict__

    except Exception as e:
        traceback.print_exc()
        return "failed"
    finally:
        pass

    
    

app.run(host = "0.0.0.0", port=80)