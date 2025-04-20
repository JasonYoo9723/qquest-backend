# qquest-backend\models\exam_model.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Exam(Base):
    __tablename__ = "t_exams"
    id = Column(Integer, primary_key=True, index=True)
    exam_code = Column(String, nullable=False)
    exam_name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    subjects = relationship("Subject", back_populates="exam")

class Subject(Base):
    __tablename__ = "t_subjects"
    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String, nullable=True)
    subject_name = Column(String, nullable=False)
    exam_id = Column(Integer, ForeignKey("t_exams.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)

    exam = relationship("Exam", back_populates="subjects")
    questions = relationship("Question", back_populates="subject")

class Question(Base):
    __tablename__ = "t_questions"
    id = Column(Integer, primary_key=True, index=True)
    question_no = Column(Integer)
    question_text = Column(Text, nullable=False)
    question_answer = Column(String, default="")
    subject_id = Column(Integer, ForeignKey("t_subjects.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("Subject", back_populates="questions")
    choices = relationship("Choice", back_populates="question")

class Choice(Base):
    __tablename__ = "t_choices"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("t_questions.id", ondelete="CASCADE"))
    choice_number = Column(Integer)
    choice_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("Question", back_populates="choices")
