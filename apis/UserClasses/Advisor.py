from UserClasses import User, Student
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey

class Advisor(User.User):

    studentList: list[Student.Student]    

    def __init__(self):
        pass

    def getAdvisor():
        return self

class AdvisorMap(User.Base):
    __tablename__="Advisor"

    advisorID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstName: Mapped[str] = mapped_column(String(50))
    lastName: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    phoneNumber: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(10))
    school: Mapped[str] = mapped_column(String(50))

class Advisor_And_StudentsMap(User.Base):
    __tablename__="Advisor_And_Students"

    advisorAndStudentsID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    advisorID: Mapped[int] = mapped_column(Integer, ForeignKey('Advisor.advisorID'))
    studentID: Mapped[int] = mapped_column(Integer, ForeignKey('Student.studentID'))