from dataclasses import dataclass
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, JSONB, numeric

@dataclass
class Transcript:
    studentid: int
    program: str = ""
    concentration: str = ""
    year: str = ""
    institution: str = ""
    coursemap: JSONB
    cumulativegpa: numeric = 0.0

class Base(DeclarativeBase):
    pass

    def getBase():
        return Base

class TranscriptMap(Base):
    __tablename__ = "transcript"

    transcriptid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    studentid: Mapped[int] = mapped_column(Integer)
    program: Mapped[str] = mapped_column(String(100))
    concentration: Mapped[str] = mapped_column(String(100))
    year: Mapped[str] = mapped_column(String(50))
    institution: Mapped[str] = mapped_column(String(150))
    coursemap: Mapped[dict] = mapped_column(JSONB, default={}, nullable=True)
    cumulativegpa: Mapped[numeric] = mapped_column(numeric)
