from sqlalchemy.orm import Session
from typing import List, Optional
import schemas
from repositories.course_repository import CourseRepository
from services.base_service import BaseService

class CourseService(BaseService):
    """
    Service layer for course business logic.
    Handles course-related operations and validations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.course_repo = CourseRepository(db)
    
    def get_all_courses(self) -> List[schemas.Course]:
        """Get all courses in the system"""
        return self.course_repo.get_all()
    
    def get_course_by_code(self, course_code: str) -> Optional[schemas.Course]:
        """
        Get a specific course by code.
        Raises ValueError if course doesn't exist.
        """
        course = self.course_repo.get_by_id(course_code)
        if not course:
            raise ValueError(f"Course with code {course_code} not found")
        return course
    
    def create_course(self, course_data: schemas.CourseCreate) -> schemas.Course:
        """
        Create a new course with validation.
        Business rules:
        - Course code must be unique
        - Credits must be positive
        """
        # Check if course already exists
        existing_course = self.course_repo.get_by_id(course_data.course_code)
        if existing_course:
            raise ValueError(f"Course with code {course_data.course_code} already exists")
        
        # Validate course data
        self._validate_course_data(course_data)
        
        return self.course_repo.create(course_data)
    
    def get_courses_by_department(self, department: str) -> List[schemas.Course]:
        """Get all courses for a specific department"""
        if not department:
            raise ValueError("Department name is required")
        
        return self.course_repo.get_by_department(department)
    
    def _validate_course_data(self, course_data: schemas.CourseCreate):
        """Validate course business rules"""
        if course_data.credits <= 0:
            raise ValueError("Course credits must be positive")
        
        if not course_data.course_title or len(course_data.course_title.strip()) == 0:
            raise ValueError("Course title cannot be empty")