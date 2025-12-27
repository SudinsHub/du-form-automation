from sqlalchemy.orm import Session
from typing import Dict, List, Any
import schemas
from repositories.remuneration_repository import RemunerationRepository
from repositories.teacher_repository import TeacherRepository
from repositories.exam_semester_repository import ExamSemesterRepository
from repositories.course_repository import CourseRepository
from services.base_service import BaseService
from services.excel_import_processor import ExcelImportProcessor, StandardExcelImportProcessor
import pandas as pd
from typing import Dict, List, Any, Optional, Set, Tuple
from fastapi import HTTPException, UploadFile
import io

class RemunerationService(BaseService):
    """
    Service layer for remuneration business logic.
    Handles complex business workflows involving multiple repositories.
    """
    
    def __init__(self, db):
        self.db = db
        self.remuneration_repo = RemunerationRepository(db)  
        self.teacher_repo = TeacherRepository(db)
        self.semester_repo = ExamSemesterRepository(db)
        self.course_repo = CourseRepository(db)

        # Initialize the Excel processor
        self.excel_processor = StandardExcelImportProcessor(
            db, 
            self.teacher_repo, 
            self.course_repo
        )
    
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
    
    def get_teacher_all_remunerations(
        self, teacher_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all remuneration data for a teacher across all semesters.
        Returns data grouped by semester.
        """
        # Validate teacher exists
        teacher = self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            raise ValueError(f"Teacher with ID {teacher_id} not found")
        
        # Get all semesters where teacher has activity
        semesters_with_activity = self.remuneration_repo.get_semesters_with_teacher_activity(teacher_id)
        
        result = []
        for semester in semesters_with_activity:
            semester_data = {
                "semester": {
                    "id": semester.id,
                    "name": semester.semester_name,
                    "year": semester.year,
                    "exam_start_date": semester.exam_start_date,
                    "exam_end_date": semester.exam_end_date,
                    "result_publish_date": semester.result_publish_date
                },
                "remunerations": self.remuneration_repo.get_teacher_remuneration(teacher_id, semester.id)
            }
            result.append(semester_data)
        
        return result
    
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
    

    # async def process_excel_import(
    #     self, 
    #     file: UploadFile, 
    #     semester_name: str, 
    #     exam_year: int
    # ) -> Dict[str, Any]:
    #     """
    #     Process Excel file containing teacher remuneration data using Template Method pattern.
        
    #     Args:
    #         file: Uploaded Excel file
    #         semester_name: Name of the semester (e.g., "1st Year 1st Semester")
    #         exam_year: Year of the examination
        
    #     Returns:
    #         Dictionary containing processed data or error information
    #     """
    #     return await self.process_excel_import_template(file, semester_name, exam_year)

    # def load_sheets(self, excel_file: io.BytesIO) -> Tuple[pd.DataFrame, pd.DataFrame]:
    #     """Load Examiners and LabCourses sheets from the Excel file."""
    #     try:
    #         examiners_df = pd.read_excel(excel_file, sheet_name='Examiners', engine='openpyxl')
    #         excel_file.seek(0)  # Reset file pointer
    #         lab_courses_df = pd.read_excel(excel_file, sheet_name='LabCourses', engine='openpyxl')
    #         return examiners_df, lab_courses_df
    #     except Exception as e:
    #         raise ValueError(f"Error reading Excel sheets: {str(e)}. Ensure 'Examiners' and 'LabCourses' sheets exist.")

    # def extract_teacher_names(self, examiners_df: pd.DataFrame, lab_courses_df: pd.DataFrame) -> Set[str]:
    #     """Extract all unique teacher names from both sheets."""
    #     all_teacher_names = set()
        
    #     # From Examiners sheet
    #     for col in ['1st Examiner', '2nd Examiner', '3rd Examiner', 'Question Typed By']:
    #         if col in examiners_df.columns:
    #             names = examiners_df[col].dropna().unique()
    #             all_teacher_names.update(names)
        
    #     # From LabCourses sheet
    #     for col in ['1st', '2nd', '3rd', '4th']:
    #         if col in lab_courses_df.columns:
    #             names = lab_courses_df[col].dropna().unique()
    #             all_teacher_names.update(names)
        
    #     return all_teacher_names

    # def extract_course_codes(self, examiners_df: pd.DataFrame, lab_courses_df: pd.DataFrame) -> Set[str]:
    #     """Extract all unique course codes from both sheets."""
    #     all_course_codes = set()
        
    #     # From Examiners sheet
    #     if 'Course' in examiners_df.columns:
    #         for course_str in examiners_df['Course'].dropna():
    #             course_code = str(course_str).split()[0] if course_str else None
    #             if course_code:
    #                 all_course_codes.add(course_code)
        
    #     # From LabCourses sheet
    #     if 'Lab Name' in lab_courses_df.columns:
    #         for course_str in lab_courses_df['Lab Name'].dropna():
    #             course_code = str(course_str).split()[0] if course_str else None
    #             if course_code:
    #                 all_course_codes.add(course_code)
        
    #     return all_course_codes

    # def verify_teachers(self, teacher_names: Set[str]) -> Tuple[Dict[str, Any], List[str]]:
    #     """Verify that all teachers exist in the database."""
    #     missing_teachers = []
    #     teacher_map = {}
        
    #     for name in teacher_names:
    #         teacher = self.teacher_repo.get_by_name(name.strip())
    #         if teacher:
    #             teacher_map[name] = teacher
    #         else:
    #             missing_teachers.append(name)
        
    #     return teacher_map, missing_teachers

    # def verify_courses(self, course_codes: Set[str]) -> Tuple[Dict[str, Any], List[str]]:
    #     """Verify that all courses exist in the database."""
    #     course_repo = CourseRepository(self.db)
    #     missing_courses = []
    #     course_map = {}
        
    #     for code in course_codes:
    #         course = course_repo.get_by_id(code)
    #         if course:
    #             course_map[code] = course
    #         else:
    #             missing_courses.append(code)
        
    #     return course_map, missing_courses

    # def initialize_teacher_data(self, teacher_map: Dict[str, Any], exam_year: int) -> Dict[str, Dict]:
    #     """Initialize the data structure for each teacher."""
    #     teachers_data = {}
        
    #     for name, teacher in teacher_map.items():
    #         teachers_data[teacher.id] = {
    #             "teacher_id": teacher.id,
    #             "teacher_name": name,
    #             "exam_year": exam_year,
    #             "questionPreparations": [],
    #             "questionModerations": [],
    #             "scriptEvaluations": [],
    #             "practicalExams": [],
    #             "vivaExams": [],
    #             "tabulations": [],
    #             "answerSheetReviews": [],
    #             "otherRemunerations": []
    #         }
        
    #     return teachers_data

    # def process_examiners_sheet(self, teachers_data: Dict[str, Dict], examiners_df: pd.DataFrame, teacher_map: Dict[str, Any]) -> Dict[str, Dict]:
    #     """Process the Examiners sheet and update teachers_data."""
    #     for idx, row in examiners_df.iterrows():
    #         course_str = row.get('Course')
    #         if pd.isna(course_str):
    #             continue
            
    #         course_code = str(course_str).split()[0]
            
    #         # Process 1st and 2nd Examiners (Question Preparation + Script Evaluation)
    #         for examiner_col, count_col in [
    #             ('1st Examiner', '1st/2nd Examiner Count'),
    #             ('2nd Examiner', '1st/2nd Examiner Count')
    #         ]:
    #             examiner_name = row.get(examiner_col)
    #             if pd.notna(examiner_name) and examiner_name in teacher_map:
    #                 teacher = teacher_map[examiner_name]
    #                 script_count = row.get(count_col, 0)
    #                 script_count = int(script_count) if pd.notna(script_count) else 0
                    
    #                 # Add Question Preparation
    #                 teachers_data[teacher.id]["questionPreparations"].append({
    #                     "course_code": course_code,
    #                     "section_type": "Full"
    #                 })
                    
    #                 # Add Script Evaluation
    #                 if script_count > 0:
    #                     teachers_data[teacher.id]["scriptEvaluations"].append({
    #                         "course_code": course_code,
    #                         "script_type": "Final",
    #                         "script_count": script_count
    #                     })
            
    #         # Process 3rd Examiner (Answer Sheet Review)
    #         examiner_3rd = row.get('3rd Examiner')
    #         if pd.notna(examiner_3rd) and examiner_3rd in teacher_map:
    #             teacher = teacher_map[examiner_3rd]
    #             answer_sheet_count = row.get('3rd Examiner Count', 0)
    #             answer_sheet_count = int(answer_sheet_count) if pd.notna(answer_sheet_count) else 0
                
    #             if answer_sheet_count > 0:
    #                 teachers_data[teacher.id]["answerSheetReviews"].append({
    #                     "course_code": course_code,
    #                     "answer_sheet_count": answer_sheet_count
    #                 })
            
    #         # Process Question Typed By (Other Remuneration)
    #         typed_by = row.get('Question Typed By')
    #         if pd.notna(typed_by) and typed_by in teacher_map:
    #             teacher = teacher_map[typed_by]
    #             pages = row.get('Pages in Question', 0)
    #             pages = int(pages) if pd.notna(pages) else 0
                
    #             if pages > 0:
    #                 teachers_data[teacher.id]["otherRemunerations"].append({
    #                     "remuneration_type": "Question Preparation and Printing",
    #                     "details": f"Question typing for {course_code}",
    #                     "page_count": pages
    #                 })
        
    #     return teachers_data

    # def process_lab_courses_sheet(self, teachers_data: Dict[str, Dict], lab_courses_df: pd.DataFrame, teacher_map: Dict[str, Any]) -> Dict[str, Dict]:
        # """Process the LabCourses sheet and update teachers_data."""
        # for idx, row in lab_courses_df.iterrows():
        #     lab_name = row.get('Lab Name')
        #     if pd.isna(lab_name):
        #         continue
            
        #     course_code = str(lab_name).split()[0]
        #     student_count = row.get('Total Students', 0)
        #     student_count = int(student_count) if pd.notna(student_count) else 0
            
        #     # Process all lab instructors (1st, 2nd, 3rd, 4th)
        #     for col in ['1st', '2nd', '3rd', '4th']:
        #         instructor_name = row.get(col)
        #         if pd.notna(instructor_name) and instructor_name in teacher_map:
        #             teacher = teacher_map[instructor_name]
                    
        #             teachers_data[teacher.id]["practicalExams"].append({
        #                 "course_code": course_code,
        #                 "student_count": student_count,
        #                 "day_count": 1
        #             })
        
        # return teachers_data

    async def process_excel_import(
        self, 
        file: UploadFile, 
        semester_name: str, 
        exam_year: int
    ) -> Dict[str, Any]:
        """
        Delegate Excel import processing to the processor.
        This maintains backward compatibility with existing code.
        """
        return await self.excel_processor.process_excel_import(
            file, 
            semester_name, 
            exam_year
        )