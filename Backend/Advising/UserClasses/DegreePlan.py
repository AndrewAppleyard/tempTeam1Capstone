from dataclasses import dataclass
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from dataclasses import dataclass, field

@dataclass
class DegreePlan:
    degree: str = ""
    institution: str = ""
    majorcode: str = ""
    credithourstotal: int = 0

    # These MUST have defaults because fields with defaults cannot come first
    notes: list[str] = field(default_factory=list)
    corecourses: list[dict] = field(default_factory=list)
    concentrations: list[dict] = field(default_factory=list)


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