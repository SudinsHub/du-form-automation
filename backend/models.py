# models.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    designation = Column(String)
    department = Column(String)
    mobile_no = Column(String)
    
    # Relationships
    question_preparations = relationship("QuestionPreparation", back_populates="teacher")
    question_moderations = relationship("QuestionModeration", back_populates="teacher")
    script_evaluations = relationship("ScriptEvaluation", back_populates="teacher")
    practical_exams = relationship("PracticalExam", back_populates="teacher")
    viva_exams = relationship("VivaExam", back_populates="teacher")
    tabulations = relationship("Tabulation", back_populates="teacher")
    answer_sheet_reviews = relationship("AnswerSheetReview", back_populates="teacher")
    other_remunerations = relationship("OtherRemuneration", back_populates="teacher")

class ExamSemester(Base):
    __tablename__ = "exam_semesters"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    semester_name = Column(String)
    exam_start_date = Column(Date)
    exam_end_date = Column(Date)
    result_publish_date = Column(Date)
    chairman_id = Column(String, ForeignKey("teachers.id"))
    
    # Relationships
    chairman = relationship("Teacher")

class Course(Base):
    __tablename__ = "courses"
    
    course_code = Column(String, primary_key=True, unique=True, index=True)
    course_title = Column(String)
    credits = Column(Float)
    department = Column(String)

class QuestionPreparation(Base):
    __tablename__ = "question_preparations"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("teachers.id"))
    exam_semester_id = Column(Integer, ForeignKey("exam_semesters.id"))
    course_code = Column(String, ForeignKey("courses.course_code"))
    section_type = Column(String)  # Full/Half
    
    # Relationships
    teacher = relationship("Teacher", back_populates="question_preparations")
    exam_semester = relationship("ExamSemester")
    course = relationship("Course")

class QuestionModeration(Base):
    __tablename__ = "question_moderations"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("teachers.id"))
    exam_semester_id = Column(Integer, ForeignKey("exam_semesters.id"))
    course_code = Column(String, ForeignKey("courses.course_code"))
    question_count = Column(Integer)
    team_member_count = Column(Integer)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="question_moderations")
    exam_semester = relationship("ExamSemester")
    course = relationship("Course")

class ScriptEvaluation(Base):
    __tablename__ = "script_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("teachers.id"))
    exam_semester_id = Column(Integer, ForeignKey("exam_semesters.id"))
    course_code = Column(String, ForeignKey("courses.course_code"))
    script_type = Column(String)  # Final/Incourse/Assignment/Presentation/Practical
    script_count = Column(Integer)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="script_evaluations")
    exam_semester = relationship("ExamSemester")
    course = relationship("Course")

class PracticalExam(Base):
    __tablename__ = "practical_exams"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("teachers.id"))
    exam_semester_id = Column(Integer, ForeignKey("exam_semesters.id"))
    course_code = Column(String, ForeignKey("courses.course_code"))
    student_count = Column(Integer)
    day_count = Column(Integer)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="practical_exams")
    exam_semester = relationship("ExamSemester")
    course = relationship("Course")

class VivaExam(Base):
    __tablename__ = "viva_exams"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("teachers.id"))
    exam_semester_id = Column(Integer, ForeignKey("exam_semesters.id"))
    course_code = Column(String, ForeignKey("courses.course_code"))
    student_count = Column(Integer)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="viva_exams")
    exam_semester = relationship("ExamSemester")
    course = relationship("Course")

class Tabulation(Base):
    __tablename__ = "tabulations"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("teachers.id"))
    exam_semester_id = Column(Integer, ForeignKey("exam_semesters.id"))
    course_code = Column(String, ForeignKey("courses.course_code"))
    student_count = Column(Integer)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="tabulations")
    exam_semester = relationship("ExamSemester")
    course = relationship("Course")

class AnswerSheetReview(Base):
    __tablename__ = "answer_sheet_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("teachers.id"))
    exam_semester_id = Column(Integer, ForeignKey("exam_semesters.id"))
    course_code = Column(String, ForeignKey("courses.course_code"))
    answer_sheet_count = Column(Integer)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="answer_sheet_reviews")
    exam_semester = relationship("ExamSemester")
    course = relationship("Course")

class OtherRemuneration(Base):
    __tablename__ = "other_remunerations"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("teachers.id"))
    exam_semester_id = Column(Integer, ForeignKey("exam_semesters.id"))
    remuneration_type = Column(String)  # Exam Committee Honorium/Stencil/Question Setter/Question Preparation and Printing
    details = Column(Text)
    page_count = Column(Integer, nullable=True)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="other_remunerations")
    exam_semester = relationship("ExamSemester")