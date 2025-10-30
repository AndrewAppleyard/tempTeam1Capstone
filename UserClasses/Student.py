from UserClasses import User
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, DateTime, String, Float, Boolean

class Student(User.User):
    classes: list[str]
    grades: list[str]
    gpa: float
    major: str
    minor: str
    registrationStatus: bool
    advisingStatus: bool
    dateAdvised: datetime
    financialHold: bool
    advisingHold: bool
    academicHold: bool

    def __init__(self):
        pass

    def getStudent():
        return self

class StudentMap(User.Base):
    __tablename__="Student"

    studentID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstName: Mapped[str] = mapped_column(String(50))
    lastName: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    phoneNumber: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(10))
    school: Mapped[str] = mapped_column(String(50))
    gpa: Mapped[float] = mapped_column(Float)
    major: Mapped[str] = mapped_column(String(50))
    minor: Mapped[str] = mapped_column(String(50))
    registrationStatus: Mapped[bool] = mapped_column(Boolean)
    advisingStatus: Mapped[bool] = mapped_column(Boolean)
    dateAdvised: Mapped[datetime] = mapped_column(DateTime)
    financialHold: Mapped[bool] = mapped_column(Boolean)
    advisingHold: Mapped[bool] = mapped_column(Boolean)
    academicHold: Mapped[bool] = mapped_column(Boolean)

