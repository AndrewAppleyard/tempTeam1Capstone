from dataclasses import dataclass
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

@dataclass
class CurrentCourse:
    section: str = ""
    courseavailability: str = ""
    deliverymode: str = ""
    meetingpattern: str = ""
    courselocation: str = ""
    instructor: str = ""
    capacity: str = ""
    enrolled: str = ""
    academicperiod: str = ""
    startdate: str = ""


class Base(DeclarativeBase):
    pass

    def getBase():
        return Base

class CurrentCourseMap(Base):
    __tablename__ = "currentcourses"

    section: Mapped[str] = mapped_column(String(30), primary_key=True)
    courseavailability: Mapped[str] = mapped_column(String(15))
    deliverymode: Mapped[str] = mapped_column(String(15))
    meetingpattern: Mapped[str] = mapped_column(String(75))
    courselocation: Mapped[str] = mapped_column(String(75))
    instructor: Mapped[str] = mapped_column(String(50))
    capacity: Mapped[str] = mapped_column(String(5))
    enrolled: Mapped[str] = mapped_column(String(5))
    academicperiod: Mapped[str] = mapped_column(String(40))
    startdate: Mapped[str] = mapped_column(String(20))