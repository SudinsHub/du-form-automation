from sqlalchemy.orm import Session
from typing import Generator
from database import get_db
from services.teacher_service import TeacherService
from services.course_service import CourseService
from services.exam_semester_service import ExamSemesterService
from services.remuneration_service import RemunerationService

def get_teacher_service(db: Session = None) -> TeacherService:
    """Dependency injection for TeacherService"""
    return TeacherService(db)

def get_course_service(db: Session = None) -> CourseService:
    """Dependency injection for CourseService"""
    return CourseService(db)

def get_exam_semester_service(db: Session = None) -> ExamSemesterService:
    """Dependency injection for ExamSemesterService"""
    return ExamSemesterService(db)

def get_remuneration_service(db: Session = None) -> RemunerationService:
    """Dependency injection for RemunerationService"""
    return RemunerationService(db)