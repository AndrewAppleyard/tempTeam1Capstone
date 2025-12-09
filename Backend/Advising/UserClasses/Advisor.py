from UserClasses import User, Student, Advisor
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Text, DateTime
import sys
from datetime import datetime, timezone 

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
    advisortype: Mapped[str] = mapped_column(String(10))

    
class Advisor_And_StudentsMap(User.Base):
    __tablename__="advisor_and_students"

    advisorandstudentid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    advisorid: Mapped[int] = mapped_column(Integer, ForeignKey('advisor.advisorid'))
    studentid: Mapped[int] = mapped_column(Integer, ForeignKey('student.studentid'))


class Appointment(User.Base):
    __tablename__ = "appointments"

    appointmentid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    advisorid: Mapped[int] = mapped_column(Integer, ForeignKey('advisor.advisorid'))
    studentid: Mapped[int] = mapped_column(Integer, ForeignKey('student.studentid'))
    starttime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    endtime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    appointmentstatus: Mapped[str] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    createdat: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc) # Use lambda to call on insertion
    )
    reminded24h: Mapped[bool] = mapped_column(default=False)
    reminded3h: Mapped[bool] = mapped_column(default=False)