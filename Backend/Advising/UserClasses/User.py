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


class UserMap(Base):
    __tablename__ = "users"

    userid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstname: Mapped[str] = mapped_column(String(50))
    lastname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50), unique=True)
    phonenumber: Mapped[str] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(10))
    school: Mapped[str] = mapped_column(String(50))