from typing import List, Optional
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
import models
import schemas

class CourseRepository(BaseRepository[models.Course]):
    """Repository for Course entity operations"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = models.Course
    
    def get_by_id(self, course_code: str) -> Optional[models.Course]:
        return self.db.query(self.model).filter(
            self.model.course_code == course_code
        ).first()
    
    def get_all(self) -> List[models.Course]:
        return self.db.query(self.model).all()
    
    def create(self, course_data: schemas.CourseCreate) -> models.Course:
        db_course = self.model(**course_data.dict())
        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)
        return db_course
    
    def update(self, course: models.Course) -> models.Course:
        self.db.commit()
        self.db.refresh(course)
        return course
    
    def delete(self, course_code: str) -> bool:
        course = self.get_by_id(course_code)
        if course:
            self.db.delete(course)
            self.db.commit()
            return True
        return False
    
    def get_by_department(self, department: str) -> List[models.Course]:
        return self.db.query(self.model).filter(
            self.model.department == department
        ).all()