from typing import List, Dict, Any
from sqlalchemy import and_
from sqlalchemy.orm import Session
import models
import schemas

class RemunerationRepository:
    """Repository for handling remuneration-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def delete_teacher_semester_data(self, teacher_id: str, semester_id: int) -> None:
        """Delete all remuneration data for a teacher in a specific semester"""
        models_to_clean = [
            models.QuestionPreparation,
            models.QuestionModeration,
            models.ScriptEvaluation,
            models.PracticalExam,
            models.VivaExam,
            models.Tabulation,
            models.AnswerSheetReview,
            models.OtherRemuneration
        ]
        
        for model in models_to_clean:
            self.db.query(model).filter(
                and_(
                    model.teacher_id == teacher_id,
                    model.exam_semester_id == semester_id
                )
            ).delete()
    
    def save_question_preparations(
        self, teacher_id: str, semester_id: int, 
        items: List[schemas.QuestionPreparationData]
    ) -> None:
        for item in items:
            db_item = models.QuestionPreparation(
                teacher_id=teacher_id,
                exam_semester_id=semester_id,
                **item.dict()
            )
            self.db.add(db_item)
    
    def save_question_moderations(
        self, teacher_id: str, semester_id: int,
        items: List[schemas.QuestionModerationData]
    ) -> None:
        for item in items:
            db_item = models.QuestionModeration(
                teacher_id=teacher_id,
                exam_semester_id=semester_id,
                **item.dict()
            )
            self.db.add(db_item)
    
    def save_script_evaluations(
        self, teacher_id: str, semester_id: int,
        items: List[schemas.ScriptEvaluationData]
    ) -> None:
        for item in items:
            db_item = models.ScriptEvaluation(
                teacher_id=teacher_id,
                exam_semester_id=semester_id,
                **item.dict()
            )
            self.db.add(db_item)
    
    def save_practical_exams(
        self, teacher_id: str, semester_id: int,
        items: List[schemas.PracticalExamData]
    ) -> None:
        for item in items:
            db_item = models.PracticalExam(
                teacher_id=teacher_id,
                exam_semester_id=semester_id,
                **item.dict()
            )
            self.db.add(db_item)
    
    def save_viva_exams(
        self, teacher_id: str, semester_id: int,
        items: List[schemas.VivaExamData]
    ) -> None:
        for item in items:
            db_item = models.VivaExam(
                teacher_id=teacher_id,
                exam_semester_id=semester_id,
                **item.dict()
            )
            self.db.add(db_item)
    
    def save_tabulations(
        self, teacher_id: str, semester_id: int,
        items: List[schemas.TabulationData]
    ) -> None:
        for item in items:
            db_item = models.Tabulation(
                teacher_id=teacher_id,
                exam_semester_id=semester_id,
                **item.dict()
            )
            self.db.add(db_item)
    
    def save_answer_sheet_reviews(
        self, teacher_id: str, semester_id: int,
        items: List[schemas.AnswerSheetReviewData]
    ) -> None:
        for item in items:
            db_item = models.AnswerSheetReview(
                teacher_id=teacher_id,
                exam_semester_id=semester_id,
                **item.dict()
            )
            self.db.add(db_item)
    
    def save_other_remunerations(
        self, teacher_id: str, semester_id: int,
        items: List[schemas.OtherRemunerationData]
    ) -> None:
        for item in items:
            db_item = models.OtherRemuneration(
                teacher_id=teacher_id,
                exam_semester_id=semester_id,
                **item.dict()
            )
            self.db.add(db_item)
    
    def get_teacher_remuneration(
        self, teacher_id: str, semester_id: int
    ) -> Dict[str, List[Any]]:
        """Get all remuneration data for a teacher in a specific semester"""
        return {
            "question_preparations": self.db.query(models.QuestionPreparation).filter(
                and_(
                    models.QuestionPreparation.teacher_id == teacher_id,
                    models.QuestionPreparation.exam_semester_id == semester_id
                )
            ).all(),
            "question_moderations": self.db.query(models.QuestionModeration).filter(
                and_(
                    models.QuestionModeration.teacher_id == teacher_id,
                    models.QuestionModeration.exam_semester_id == semester_id
                )
            ).all(),
            "script_evaluations": self.db.query(models.ScriptEvaluation).filter(
                and_(
                    models.ScriptEvaluation.teacher_id == teacher_id,
                    models.ScriptEvaluation.exam_semester_id == semester_id
                )
            ).all(),
            "practical_exams": self.db.query(models.PracticalExam).filter(
                and_(
                    models.PracticalExam.teacher_id == teacher_id,
                    models.PracticalExam.exam_semester_id == semester_id
                )
            ).all(),
            "viva_exams": self.db.query(models.VivaExam).filter(
                and_(
                    models.VivaExam.teacher_id == teacher_id,
                    models.VivaExam.exam_semester_id == semester_id
                )
            ).all(),
            "tabulations": self.db.query(models.Tabulation).filter(
                and_(
                    models.Tabulation.teacher_id == teacher_id,
                    models.Tabulation.exam_semester_id == semester_id
                )
            ).all(),
            "answer_sheet_reviews": self.db.query(models.AnswerSheetReview).filter(
                and_(
                    models.AnswerSheetReview.teacher_id == teacher_id,
                    models.AnswerSheetReview.exam_semester_id == semester_id
                )
            ).all(),
            "other_remunerations": self.db.query(models.OtherRemuneration).filter(
                and_(
                    models.OtherRemuneration.teacher_id == teacher_id,
                    models.OtherRemuneration.exam_semester_id == semester_id
                )
            ).all(),
        }
    
    def get_teachers_with_semester_activity(
        self, semester_id: int
    ) -> List[models.Teacher]:
        """Get all teachers who have submitted remuneration for a semester"""
        return self.db.query(models.Teacher).outerjoin(
            models.QuestionPreparation,
            models.Teacher.id == models.QuestionPreparation.teacher_id
        ).outerjoin(
            models.QuestionModeration,
            models.Teacher.id == models.QuestionModeration.teacher_id
        ).outerjoin(
            models.ScriptEvaluation,
            models.Teacher.id == models.ScriptEvaluation.teacher_id
        ).outerjoin(
            models.PracticalExam,
            models.Teacher.id == models.PracticalExam.teacher_id
        ).outerjoin(
            models.VivaExam,
            models.Teacher.id == models.VivaExam.teacher_id
        ).outerjoin(
            models.Tabulation,
            models.Teacher.id == models.Tabulation.teacher_id
        ).outerjoin(
            models.AnswerSheetReview,
            models.Teacher.id == models.AnswerSheetReview.teacher_id
        ).outerjoin(
            models.OtherRemuneration,
            models.Teacher.id == models.OtherRemuneration.teacher_id
        ).filter(
            (models.QuestionPreparation.exam_semester_id == semester_id) |
            (models.QuestionModeration.exam_semester_id == semester_id) |
            (models.ScriptEvaluation.exam_semester_id == semester_id) |
            (models.PracticalExam.exam_semester_id == semester_id) |
            (models.VivaExam.exam_semester_id == semester_id) |
            (models.Tabulation.exam_semester_id == semester_id) |
            (models.AnswerSheetReview.exam_semester_id == semester_id) |
            (models.OtherRemuneration.exam_semester_id == semester_id)
        ).distinct(models.Teacher.id).all()
    
    def get_semesters_with_teacher_activity(
        self, teacher_id: str
    ) -> List[models.ExamSemester]:
        """Get all semesters where a teacher has submitted remuneration"""
        return self.db.query(models.ExamSemester).outerjoin(
            models.QuestionPreparation,
            models.ExamSemester.id == models.QuestionPreparation.exam_semester_id
        ).outerjoin(
            models.QuestionModeration,
            models.ExamSemester.id == models.QuestionModeration.exam_semester_id
        ).outerjoin(
            models.ScriptEvaluation,
            models.ExamSemester.id == models.ScriptEvaluation.exam_semester_id
        ).outerjoin(
            models.PracticalExam,
            models.ExamSemester.id == models.PracticalExam.exam_semester_id
        ).outerjoin(
            models.VivaExam,
            models.ExamSemester.id == models.VivaExam.exam_semester_id
        ).outerjoin(
            models.Tabulation,
            models.ExamSemester.id == models.Tabulation.exam_semester_id
        ).outerjoin(
            models.AnswerSheetReview,
            models.ExamSemester.id == models.AnswerSheetReview.exam_semester_id
        ).outerjoin(
            models.OtherRemuneration,
            models.ExamSemester.id == models.OtherRemuneration.exam_semester_id
        ).filter(
            (models.QuestionPreparation.teacher_id == teacher_id) |
            (models.QuestionModeration.teacher_id == teacher_id) |
            (models.ScriptEvaluation.teacher_id == teacher_id) |
            (models.PracticalExam.teacher_id == teacher_id) |
            (models.VivaExam.teacher_id == teacher_id) |
            (models.Tabulation.teacher_id == teacher_id) |
            (models.AnswerSheetReview.teacher_id == teacher_id) |
            (models.OtherRemuneration.teacher_id == teacher_id)
        ).distinct(models.ExamSemester.id).all()
    
    def commit(self) -> None:
        """Commit the current transaction"""
        self.db.commit()
