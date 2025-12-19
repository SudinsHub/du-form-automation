from typing import List, Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
import models
import schemas

class ExamSemesterRepository(BaseRepository[models.ExamSemester]):
    """Repository for ExamSemester entity operations"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = models.ExamSemester
    
    def get_by_id(self, semester_id: int) -> Optional[models.ExamSemester]:
        return self.db.query(self.model).filter(
            self.model.id == semester_id
        ).first()
    
    def get_all(self) -> List[models.ExamSemester]:
        return self.db.query(self.model).all()
    
    def create(self, semester_data: schemas.ExamSemesterCreate) -> models.ExamSemester:
        db_semester = self.model(**semester_data.dict())
        self.db.add(db_semester)
        self.db.commit()
        self.db.refresh(db_semester)
        return db_semester
    
    def update(self, semester: models.ExamSemester) -> models.ExamSemester:
        self.db.commit()
        self.db.refresh(semester)
        return semester
    
    def delete(self, semester_id: int) -> bool:
        semester = self.get_by_id(semester_id)
        if semester:
            self.db.delete(semester)
            self.db.commit()
            return True
        return False
    
    def get_by_year_and_name(self, year: int, semester_name: str) -> Optional[models.ExamSemester]:
        """Get semester by year and name"""
        return self.db.query(self.model).filter(
            and_(
                self.model.year == int(year),
                self.model.semester_name == semester_name
            )
        ).first()
    
    

