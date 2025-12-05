from UserClasses import User
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, DateTime, String, Float, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

class Student(User.User):
    grades: list[str]
    gpa: float
    major: str
    minor: str
    registrationstatus: bool
    advisingstatus: bool
    dateadvised: datetime
    financialhold: bool
    advisinghold: bool
    academichold: bool
    classes: list[dict]

    def __init__(self):
        pass

    def getStudent():
        return self

class StudentMap(User.Base):
    __tablename__="student"

    studentid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstname: Mapped[str] = mapped_column(String(50))
    lastname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    phonenumber: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(10))
    school: Mapped[str] = mapped_column(String(50))

    gpa: Mapped[float] = mapped_column(Float)
    major: Mapped[str] = mapped_column(String(50))
    majorconcentration: Mapped[str] = mapped_column(String(50), default="")
    minor: Mapped[str] = mapped_column(String(50), default="")
    classstanding: Mapped[str] = mapped_column(String(50), default="")
    financialhold: Mapped[bool] = mapped_column(Boolean, default=False)
    advisinghold: Mapped[bool] = mapped_column(Boolean, default=False)
    academichold: Mapped[bool] = mapped_column(Boolean, default=False)
    registrationstatus: Mapped[bool] = mapped_column(Boolean, default=False)
    advisingstatus: Mapped[bool] = mapped_column(Boolean, default=False)
    activestatus: Mapped[bool] = mapped_column(Boolean, default=True)
    dateadvised: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    classes: Mapped[dict] = mapped_column(JSONB, default={}, nullable=True)