from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Teacher schemas
class TeacherBase(BaseModel):
    id: str # added this line
    name: str
    designation: str
    department: str
    mobile_no: Optional[str] = None

class TeacherCreate(TeacherBase):
    pass

class Teacher(TeacherBase):
    pass

# Course schemas
class CourseBase(BaseModel):
    dept: str
    course_code: str
    course_title: str
    credits: float
    department: str

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    pass

# ExamSemester schemas
class ExamSemesterBase(BaseModel):
    year: int
    semester_name: str
    exam_start_date: Optional[date] = None
    exam_end_date: Optional[date] = None
    result_publish_date: Optional[date] = None
    chairman_id: Optional[int] = None

class ExamSemesterCreate(ExamSemesterBase):
    pass

class ExamSemester(ExamSemesterBase):
    id: int
    
    class Config:
        from_attributes = True

# Remuneration schemas
class QuestionPreparationData(BaseModel):
    course_code: str
    section_type: str

class QuestionModerationData(BaseModel):
    course_code: str
    question_count: int
    team_member_count: int

class ScriptEvaluationData(BaseModel):
    course_code: str
    script_type: str
    script_count: int

class PracticalExamData(BaseModel):
    course_code: str
    student_count: int
    day_count: int

class VivaExamData(BaseModel):
    course_code: str
    student_count: int

class TabulationData(BaseModel):
    course_code: str
    student_count: int

class AnswerSheetReviewData(BaseModel):
    course_code: str
    answer_sheet_count: int

class OtherRemunerationData(BaseModel):
    remuneration_type: str
    details: str
    page_count: Optional[int] = None

class RemunerationSubmission(BaseModel):
    teacher_id: str
    exam_semester_id: int
    question_preparations: List[QuestionPreparationData] = []
    question_moderations: List[QuestionModerationData] = []
    script_evaluations: List[ScriptEvaluationData] = []
    practical_exams: List[PracticalExamData] = []
    viva_exams: List[VivaExamData] = []
    tabulations: List[TabulationData] = []
    answer_sheet_reviews: List[AnswerSheetReviewData] = []
    other_remunerations: List[OtherRemunerationData] = []

class PDFExportRequest(BaseModel):
    teacher_id: str
    exam_semester_id: int

class CumulativeReportRequest(BaseModel):
    exam_semester_id: int
