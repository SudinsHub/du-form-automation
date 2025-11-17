from typing import List, Optional
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
import models
import schemas

class TeacherRepository(BaseRepository[models.Teacher]):
    """Repository for Teacher entity operations"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = models.Teacher
    
    def get_by_id(self, teacher_id: str) -> Optional[models.Teacher]:
        return self.db.query(self.model).filter(
            self.model.id == teacher_id
        ).first()
    
    def get_by_name(self, teacher_name: str) -> Optional[models.Teacher]:
        return self.db.query(self.model).filter(
            self.model.name.contains(teacher_name)
        ).first()
    
    def get_all(self) -> List[models.Teacher]:
        return self.db.query(self.model).all()
    
    def create(self, teacher_data: schemas.TeacherCreate) -> models.Teacher:
        db_teacher = self.model(**teacher_data.dict())
        self.db.add(db_teacher)
        self.db.commit()
        self.db.refresh(db_teacher)
        return db_teacher
    
    def update(self, teacher: models.Teacher) -> models.Teacher:
        self.db.commit()
        self.db.refresh(teacher)
        return teacher
    
    def delete(self, teacher_id: str) -> bool:
        teacher = self.get_by_id(teacher_id)
        if teacher:
            self.db.delete(teacher)
            self.db.commit()
            return True
        return False
    
    def get_by_department(self, department: str) -> List[models.Teacher]:
        return self.db.query(self.model).filter(
            self.model.department == department
        ).all()
    
    def exists(self, teacher_id: str) -> bool:
        """Check if teacher exists"""
        return self.db.query(self.model).filter(
            self.model.id == teacher_id
        ).count() > 0