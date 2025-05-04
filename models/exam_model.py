# models\exam_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# ✅ 1. 자격증 마스터 테이블
class Exam(Base):
    __tablename__ = 't_exams'

    id = Column(Integer, primary_key=True, index=True)
    exam_code = Column(String(50), unique=True, index=True, nullable=False)
    exam_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    rounds = relationship('ExamRound', back_populates='exam')


# ✅ 2. 과목 마스터 테이블
class Subject(Base):
    __tablename__ = 't_subjects'

    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String(50), unique=True, nullable=False)
    subject_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ✅ 3. 자격증 회차 테이블
class ExamRound(Base):
    __tablename__ = 't_exam_rounds'

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey('t_exams.id'), nullable=False)
    year = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    exam = relationship('Exam', back_populates='rounds')
    subject_links = relationship('RoundSubject', back_populates='exam_round')


# ✅ 4. 회차-과목 연결 테이블
class RoundSubject(Base):
    __tablename__ = 't_round_subjects'

    id = Column(Integer, primary_key=True)
    exam_round_id = Column(Integer, ForeignKey('t_exam_rounds.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('t_subjects.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    exam_round = relationship('ExamRound', back_populates='subject_links')
    subject = relationship('Subject')
    questions = relationship('Question', back_populates='round_subject')


# ✅ 5. 문제 테이블
class Question(Base):
    __tablename__ = 't_questions'

    id = Column(Integer, primary_key=True)
    round_subject_id = Column(Integer, ForeignKey('t_round_subjects.id'), nullable=False)
    question_no = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    question_answer = Column(String(10))  # nullable=True가 기본입니다.
    created_at = Column(DateTime, default=datetime.utcnow)

    round_subject = relationship('RoundSubject', back_populates='questions')
    choices = relationship('Choice', back_populates='question', cascade='all, delete-orphan')


# ✅ 6. 보기 테이블
class Choice(Base):
    __tablename__ = 't_choices'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('t_questions.id'), nullable=False)
    choice_number = Column(Integer)
    choice_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship('Question', back_populates='choices')
