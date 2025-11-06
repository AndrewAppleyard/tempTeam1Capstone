from dataclasses import dataclass
from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

@dataclass
class User:
    userid: int
    firstname: str
    lastname: str
    email: str
    phonenumber: int
    role: str
    school: str

    def __init__(self):
        pass


class Base(DeclarativeBase):
    pass

    def getBase():
        return Base
