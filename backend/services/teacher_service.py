from sqlalchemy.orm import Session
from typing import List, Optional
import schemas
from repositories.teacher_repository import TeacherRepository
from services.base_service import BaseService

class TeacherService(BaseService):
    """
    Service layer for teacher business logic.
    Handles validation, business rules, and orchestration.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.teacher_repo = TeacherRepository(db)
    
    def get_all_teachers(self) -> List[schemas.Teacher]:
        """
        Get all teachers from the system.
        Business rule: Return all active teachers.
        """
        teachers = self.teacher_repo.get_all()
        return teachers
    
    def get_teacher_by_id(self, teacher_id: str) -> Optional[schemas.Teacher]:
        """
        Get a specific teacher by ID.
        Raises ValueError if teacher doesn't exist.
        """
        teacher = self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            raise ValueError(f"Teacher with ID {teacher_id} not found")
        return teacher

    def get_teacher_by_name(self, teacher_name: str) -> Optional[schemas.Teacher]:

        teacher = self.teacher_repo.get_by_name(teacher_name)
        if not teacher:
            raise ValueError(f"Teacher with name {teacher_name} not found")
        return teacher
    
    def create_teacher(self, teacher_data: schemas.TeacherCreate) -> schemas.Teacher:
        """
        Create a new teacher with validation.
        Business rules:
        - Teacher ID must be unique
        - Mobile number format validation could be added
        """
        # Check if teacher already exists
        existing_teacher = self.teacher_repo.get_by_id(teacher_data.id)
        if existing_teacher:
            raise ValueError(f"Teacher with ID {teacher_data.id} already exists")
        
        # Additional business validation can go here
        self._validate_teacher_data(teacher_data)
        
        return self.teacher_repo.create(teacher_data)
    
    def get_teachers_by_department(self, department: str) -> List[schemas.Teacher]:
        """
        Get all teachers in a specific department.
        Business rule: Filter by exact department match.
        """
        if not department:
            raise ValueError("Department name is required")
        
        return self.teacher_repo.get_by_department(department)
    
    def teacher_exists(self, teacher_id: str) -> bool:
        """Check if a teacher exists in the system"""
        return self.teacher_repo.exists(teacher_id)
    
    def _validate_teacher_data(self, teacher_data: schemas.TeacherCreate):
        """
        Private method for business validation.
        Can be extended with more rules.
        """
        if not teacher_data.name or len(teacher_data.name.strip()) == 0:
            raise ValueError("Teacher name cannot be empty")
        
        if not teacher_data.designation:
            raise ValueError("Teacher designation is required")