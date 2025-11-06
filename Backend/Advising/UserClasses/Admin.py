from UserClasses import User, Student, Advisor
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

class Admin(User.User):
    studentList: list[Student.Student]
    advisorList: list[Advisor.Advisor]
    

    def __init__(self):
        pass

class AdminMap(User.Base):
    __tablename__="Admin"

    adminid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstname: Mapped[str] = mapped_column(String(50))
    lastname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    phonenumber: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(10))
    school: Mapped[str] = mapped_column(String(50))