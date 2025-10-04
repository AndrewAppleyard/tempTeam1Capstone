from UserClasses import User
from datetime import datetime

class Student(User.User):
    classes: list[str]
    grades: list[str]
    gpa: float
    advisor: str
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

