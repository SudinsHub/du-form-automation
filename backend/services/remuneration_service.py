from sqlalchemy.orm import Session
from typing import Dict, List, Any
import schemas
from repositories.remuneration_repository import RemunerationRepository
from repositories.teacher_repository import TeacherRepository
from repositories.exam_semester_repository import ExamSemesterRepository
from services.base_service import BaseService

class RemunerationService(BaseService):
    """
    Service layer for remuneration business logic.
    Handles complex business workflows involving multiple repositories.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.remuneration_repo = RemunerationRepository(db)
        self.teacher_repo = TeacherRepository(db)
        self.semester_repo = ExamSemesterRepository(db)
    
    def submit_remuneration(
        self, data: schemas.RemunerationSubmission
    ) -> Dict[str, str]:
        """
        Submit remuneration data for a teacher.
        Business rules:
        - Teacher must exist
        - Semester must exist
        - Replaces any existing data for this teacher+semester
        - All operations must succeed or rollback
        """
        # Validate teacher exists
        teacher = self.teacher_repo.get_by_id(data.teacher_id)
        if not teacher:
            raise ValueError(f"Teacher with ID {data.teacher_id} not found")
        
        # Validate semester exists
        semester = self.semester_repo.get_by_id(data.exam_semester_id)
        if not semester:
            raise ValueError(f"Semester with ID {data.exam_semester_id} not found")
        
        try:
            # Delete existing records (business rule: replace, not append)
            self.remuneration_repo.delete_teacher_semester_data(
                data.teacher_id, data.exam_semester_id
            )
            
            # Save all new records
            self._save_all_remuneration_data(data)
            
            # Commit transaction
            self.remuneration_repo.commit()
            
            return {
                "message": "Remuneration submitted successfully",
                "teacher_id": data.teacher_id,
                "semester_id": data.exam_semester_id
            }
            
        except Exception as e:
            # Rollback will happen automatically
            raise ValueError(f"Failed to submit remuneration: {str(e)}")
    
    def get_teacher_remuneration(
        self, teacher_id: str, semester_id: int
    ) -> Dict[str, List[Any]]:
        """
        Get all remuneration data for a teacher in a specific semester.
        Validates that both teacher and semester exist.
        """
        # Validate teacher exists
        teacher = self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            raise ValueError(f"Teacher with ID {teacher_id} not found")
        
        # Validate semester exists
        semester = self.semester_repo.get_by_id(semester_id)
        if not semester:
            raise ValueError(f"Semester with ID {semester_id} not found")
        
        return self.remuneration_repo.get_teacher_remuneration(
            teacher_id, semester_id
        )
    
    def get_cumulative_report(self, semester_id: int) -> List[Dict[str, Any]]:
        """
        Generate cumulative report for all teachers in a semester.
        Business rule: Only include teachers with at least one remuneration entry.
        """
        # Validate semester exists
        semester = self.semester_repo.get_by_id(semester_id)
        if not semester:
            raise ValueError(f"Semester with ID {semester_id} not found")
        
        # Get all teachers with activity in this semester
        teachers = self.remuneration_repo.get_teachers_with_semester_activity(
            semester_id
        )
        
        # Build report data
        report_data = []
        for teacher in teachers:
            teacher_data = self.remuneration_repo.get_teacher_remuneration(
                teacher.id, semester_id
            )
            
            # Calculate total remuneration (business logic)
            total_amount = self._calculate_total_remuneration(teacher_data)
            
            report_data.append({
                "teacher": teacher,
                "details": teacher_data,
                "total_amount": total_amount  # Service layer adds computed data
            })
        
        return report_data
    
    def _save_all_remuneration_data(self, data: schemas.RemunerationSubmission):
        """Private method to save all remuneration types"""
        if data.question_preparations:
            self.remuneration_repo.save_question_preparations(
                data.teacher_id, data.exam_semester_id, data.question_preparations
            )
        
        if data.question_moderations:
            self.remuneration_repo.save_question_moderations(
                data.teacher_id, data.exam_semester_id, data.question_moderations
            )
        
        if data.script_evaluations:
            self.remuneration_repo.save_script_evaluations(
                data.teacher_id, data.exam_semester_id, data.script_evaluations
            )
        
        if data.practical_exams:
            self.remuneration_repo.save_practical_exams(
                data.teacher_id, data.exam_semester_id, data.practical_exams
            )
        
        if data.viva_exams:
            self.remuneration_repo.save_viva_exams(
                data.teacher_id, data.exam_semester_id, data.viva_exams
            )
        
        if data.tabulations:
            self.remuneration_repo.save_tabulations(
                data.teacher_id, data.exam_semester_id, data.tabulations
            )
        
        if data.answer_sheet_reviews:
            self.remuneration_repo.save_answer_sheet_reviews(
                data.teacher_id, data.exam_semester_id, data.answer_sheet_reviews
            )
        
        if data.other_remunerations:
            self.remuneration_repo.save_other_remunerations(
                data.teacher_id, data.exam_semester_id, data.other_remunerations
            )
    
    def _calculate_total_remuneration(self, teacher_data: Dict[str, List[Any]]) -> float:
        """
        Calculate total remuneration amount.
        This is business logic that belongs in the service layer.
        You can customize rates based on your business rules.
        """
        total = 0.0
        
        # Example calculation - adjust rates as per your requirements
        # Question preparation: 500 per full section, 250 per half
        for prep in teacher_data.get('question_preparations', []):
            if prep.section_type.lower() == 'full':
                total += 500.0
            else:
                total += 250.0
        
        # Question moderation: 100 per question / team member count
        for mod in teacher_data.get('question_moderations', []):
            if mod.team_member_count > 0:
                total += (mod.question_count * 100.0) / mod.team_member_count
        
        # Script evaluation: varies by type
        for script in teacher_data.get('script_evaluations', []):
            rate_map = {
                'final': 15.0,
                'incourse': 5.0,
                'assignment': 5.0,
                'presentation': 10.0,
                'practical': 10.0
            }
            rate = rate_map.get(script.script_type.lower(), 10.0)
            total += script.script_count * rate
        
        # Practical exams: 200 per day per student (example)
        for practical in teacher_data.get('practical_exams', []):
            total += practical.student_count * practical.day_count * 2.0
        
        # Viva exams: 10 per student
        for viva in teacher_data.get('viva_exams', []):
            total += viva.student_count * 10.0
        
        # Tabulation: 5 per student
        for tab in teacher_data.get('tabulations', []):
            total += tab.student_count * 5.0
        
        # Answer sheet review: 20 per sheet
        for review in teacher_data.get('answer_sheet_reviews', []):
            total += review.answer_sheet_count * 20.0
        
        # Other remunerations: calculate based on page count or fixed amount
        for other in teacher_data.get('other_remunerations', []):
            if other.page_count:
                total += other.page_count * 10.0  # 10 per page
            else:
                total += 500.0  # Fixed amount for non-page based
        
        return total