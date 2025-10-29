from dataclasses import dataclass

@dataclass
class CurrentCourse:
    section: str = ""
    availability: str = ""
    deliveryMode: str = ""
    instructor: str = ""
    meetingPattern: str = ""
    academicPeriod: str = ""
    capacity: str = ""
    location: str = ""
    startDate: str = ""
    enrolled: str = ""