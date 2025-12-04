from dataclasses import dataclass
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB

@dataclass
class DegreePlan:
    degree: str
    institution: str
    majorcode: str
    credithourstotal: int
    notes: list[str]
    corecourses: list[dict]
    concentrations: list[dict]

class Base(DeclarativeBase):
    pass

    def getBase():
        return Base


class DegreePlanMap(Base):
    __tablename__ = "degreeplans"

    degree: Mapped[str] = mapped_column(String(50), primary_key=True)
    institution: Mapped[str] = mapped_column(String(50))
    majorcode: Mapped[str] = mapped_column(String(10))
    credithourstotal: Mapped[int] = mapped_column(Integer)
    notes: Mapped[list] = mapped_column(JSONB, default={}, nullable=True)
    corecourses: Mapped[list] = mapped_column(JSONB, default={}, nullable=True)
    concentrations: Mapped[list] = mapped_column(JSONB, default={}, nullable=True)