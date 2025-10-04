from UserClasses import User, Student, Advisor

class Admin(User.User):
    studentList: list[Student.Student]
    advisorList: list[Advisor.Advisor]

    def __init__(self):
        pass