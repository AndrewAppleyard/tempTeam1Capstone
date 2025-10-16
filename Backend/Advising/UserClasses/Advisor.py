from UserClasses import User, Student, Advisor
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
import sys


class Advisor(User.User):
    studentList: list[Student.Student]
    
    

    def __init__(self):
        pass

class AdvisorMap(User.Base):
    __tablename__="advisor"

    advisorid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstname: Mapped[str] = mapped_column(String(50))
    lastname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    phonenumber: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(10))
    school: Mapped[str] = mapped_column(String(50))

    
class Advisor_And_StudentsMap(User.Base):
    __tablename__="advisor_and_students"

    advisorandstudentid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    advisorid: Mapped[int] = mapped_column(Integer, ForeignKey('advisor.advisorid'))
    studentid: Mapped[int] = mapped_column(Integer, ForeignKey('student.studentid'))