from sqlalchemy.orm import Session
from typing import List, Optional
import schemas
from repositories.exam_semester_repository import ExamSemesterRepository
from services.base_service import BaseService

class ExamSemesterService(BaseService):
    """
    Service layer for exam semester business logic.
    Manages semester lifecycle and validations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.semester_repo = ExamSemesterRepository(db)
    
    def get_all_semesters(self) -> List[schemas.ExamSemester]:
        """Get all exam semesters"""
        return self.semester_repo.get_all()
    
    def get_semester_by_id(self, semester_id: int) -> Optional[schemas.ExamSemester]:
        """
        Get semester by ID.
        Raises ValueError if not found.
        """
        semester = self.semester_repo.get_by_id(semester_id)
        if not semester:
            raise ValueError(f"Semester with ID {semester_id} not found")
        return semester
    
    def get_semester_by_year_and_name(
        self, year: int, semester_name: str
    ) -> Optional[schemas.ExamSemester]:
        """
        Get semester by year and name.
        Returns None if not found.
        """
        return self.semester_repo.get_by_year_and_name(year, semester_name)
    
    def create_semester(
        self, semester_data: schemas.ExamSemesterCreate
    ) -> schemas.ExamSemester:
        """
        Create a new semester with validation.
        Business rules:
        - Year + semester_name combination must be unique
        - Dates must be logical (start < end < publish)
        """
        # Check if semester already exists
        existing = self.semester_repo.get_by_year_and_name(
            semester_data.year, semester_data.semester_name
        )
        if existing:
            raise ValueError(
                f"Semester {semester_data.semester_name} {semester_data.year} already exists"
            )
        
        # Validate semester data
        self._validate_semester_data(semester_data)
        
        return self.semester_repo.create(semester_data)
    
    def get_or_create_semester(
        self, year: int, semester_name: str
    ) -> schemas.ExamSemester:
        """
        Get existing semester or create new one if it doesn't exist.
        Business rule: Ensure semester uniqueness by year+name.
        """
        semester = self.semester_repo.get_by_year_and_name(year, semester_name)
        
        if not semester:
            semester = self.semester_repo.create(
                schemas.ExamSemesterCreate(
                    year=year, 
                    semester_name=semester_name
                )
            )
        
        return semester
    
    def _validate_semester_data(self, semester_data: schemas.ExamSemesterCreate):
        """Validate semester business rules"""
        if semester_data.year < 2000 or semester_data.year > 2100:
            raise ValueError("Invalid year")
        
        if not semester_data.semester_name:
            raise ValueError("Semester name is required")
        
        # Validate date logic if dates are provided
        if semester_data.exam_start_date and semester_data.exam_end_date:
            if semester_data.exam_start_date > semester_data.exam_end_date:
                raise ValueError("Exam start date must be before end date")
        
        if semester_data.exam_end_date and semester_data.result_publish_date:
            if semester_data.exam_end_date > semester_data.result_publish_date:
                raise ValueError("Result publish date must be after exam end date")
