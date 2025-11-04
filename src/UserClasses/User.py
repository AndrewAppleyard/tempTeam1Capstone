from dataclasses import dataclass
from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

@dataclass
class User:
    userID: int
    firstName: str
    lastName: str
    email: str
    phoneNumber: int
    role: str
    school: str

    def __init__(self):
        pass


class Base(DeclarativeBase):
    pass

    def getBase():
        return Base