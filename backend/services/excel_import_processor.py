"""
Excel Import Processing using Template Method Pattern
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Set, Tuple
import pandas as pd
import io
from fastapi import UploadFile


class ExcelImportProcessor(ABC):
    """
    Abstract base class defining the template for Excel import processing.
    Uses Template Method pattern to define the skeleton of the import algorithm.
    """
    
    def __init__(self, db_session, teacher_repo, course_repo):
        self.db = db_session
        self.teacher_repo = teacher_repo
        self.course_repo = course_repo
    
    async def process_excel_import(
        self, 
        file: UploadFile, 
        semester_name: str, 
        exam_year: int
    ) -> Dict[str, Any]:
        """
        Template method defining the skeleton of the import process.
        This method orchestrates the entire import workflow.
        """
        try:
            # Step 1: Read and validate Excel file
            excel_file = await self._read_excel_file(file)
            dataframes = self._load_required_sheets(excel_file)
            
            # Step 2: Extract and validate teachers
            all_teacher_names = self._extract_teacher_names(dataframes)
            teacher_map, missing_teachers = self._validate_teachers(all_teacher_names)
            
            if missing_teachers:
                return self._create_error_response(
                    "Some teachers not found in database",
                    missing_teachers=missing_teachers
                )
            
            # Step 3: Extract and validate courses
            all_course_codes = self._extract_course_codes(dataframes)
            course_map, missing_courses = self._validate_courses(all_course_codes)
            
            if missing_courses:
                return self._create_error_response(
                    "Some courses not found in database",
                    missing_courses=missing_courses
                )
            
            # Step 4: Build remuneration data for each teacher
            teachers_data = self._initialize_teacher_data(teacher_map, exam_year)
            self._process_remuneration_data(dataframes, teachers_data, teacher_map, course_map)
            
            # Step 5: Return success response
            return self._create_success_response(
                teachers_data, 
                semester_name, 
                exam_year
            )
            
        except Exception as e:
            raise ValueError(f"Error processing Excel file: {str(e)}")
    
    # Abstract methods - must be implemented by subclasses
    
    @abstractmethod
    def _load_required_sheets(self, excel_file: io.BytesIO) -> Dict[str, pd.DataFrame]:
        """Load required sheets from Excel file. Returns dict of sheet_name -> DataFrame."""
        pass
    
    @abstractmethod
    def _extract_teacher_names(self, dataframes: Dict[str, pd.DataFrame]) -> Set[str]:
        """Extract all unique teacher names from the dataframes."""
        pass
    
    @abstractmethod
    def _extract_course_codes(self, dataframes: Dict[str, pd.DataFrame]) -> Set[str]:
        """Extract all unique course codes from the dataframes."""
        pass
    
    @abstractmethod
    def _process_remuneration_data(
        self, 
        dataframes: Dict[str, pd.DataFrame],
        teachers_data: Dict[str, Dict],
        teacher_map: Dict[str, Any],
        course_map: Dict[str, Any]
    ):
        """Process dataframes and populate teachers_data with remuneration information."""
        pass
    
    # Concrete methods - shared implementation
    
    async def _read_excel_file(self, file: UploadFile) -> io.BytesIO:
        """Read uploaded Excel file into memory."""
        contents = await file.read()
        return io.BytesIO(contents)
    
    def _validate_teachers(self, teacher_names: Set[str]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validate that all teachers exist in database.
        Returns: (teacher_map, missing_teachers)
        """
        missing_teachers = []
        teacher_map = {}
        
        for name in teacher_names:
            teacher = self.teacher_repo.get_by_name(name.strip())
            if teacher:
                teacher_map[name] = teacher
            else:
                missing_teachers.append(name)
        
        return teacher_map, missing_teachers
    
    def _validate_courses(self, course_codes: Set[str]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validate that all courses exist in database.
        Returns: (course_map, missing_courses)
        """
        missing_courses = []
        course_map = {}
        
        for code in course_codes:
            course = self.course_repo.get_by_id(code)
            if course:
                course_map[code] = course
            else:
                missing_courses.append(code)
        
        return course_map, missing_courses
    
    def _initialize_teacher_data(
        self, 
        teacher_map: Dict[str, Any], 
        exam_year: int
    ) -> Dict[str, Dict]:
        """Initialize data structure for all teachers."""
        teachers_data = {}
        
        for name, teacher in teacher_map.items():
            teachers_data[teacher.id] = {
                "teacher_id": teacher.id,
                "teacher_name": name,
                "exam_year": exam_year,
                "questionPreparations": [],
                "questionModerations": [],
                "scriptEvaluations": [],
                "practicalExams": [],
                "vivaExams": [],
                "tabulations": [],
                "answerSheetReviews": [],
                "otherRemunerations": []
            }
        
        return teachers_data
    
    def _create_error_response(
        self, 
        message: str, 
        missing_teachers: List[str] = None,
        missing_courses: List[str] = None
    ) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "status": "error",
            "code": 404,
            "message": message,
            "missing_teachers": missing_teachers or [],
            "teachers_data": [],
            "missing_courses": missing_courses or []
        }
    
    def _create_success_response(
        self, 
        teachers_data: Dict[str, Dict],
        semester_name: str,
        exam_year: int
    ) -> Dict[str, Any]:
        """Create standardized success response."""
        result_data = list(teachers_data.values())
        
        return {
            "status": "success",
            "code": 200,
            "message": f"Successfully processed data for {len(result_data)} teachers",
            "semester_name": semester_name,
            "exam_year": exam_year,
            "teachers_data": result_data,
            "missing_teachers": [],
            "missing_courses": []
        }
    
    # Helper methods for subclasses
    
    def _extract_course_code_from_string(self, course_str: str) -> str:
        """Extract course code from a course string (e.g., 'CSE-4101 AI' -> 'CSE-4101')."""
        return str(course_str).split()[0] if course_str else None
    
    def _safe_int_conversion(self, value, default: int = 0) -> int:
        """Safely convert value to int, returning default if conversion fails."""
        try:
            return int(value) if pd.notna(value) else default
        except (ValueError, TypeError):
            return default


class StandardExcelImportProcessor(ExcelImportProcessor):
    """
    Concrete implementation for the standard Excel format with 
    'Examiners' and 'LabCourses' sheets.
    """
    
    def _load_required_sheets(self, excel_file: io.BytesIO) -> Dict[str, pd.DataFrame]:
        """Load Examiners and LabCourses sheets."""
        try:
            examiners_df = pd.read_excel(excel_file, sheet_name='Examiners', engine='openpyxl')
            excel_file.seek(0)
            lab_courses_df = pd.read_excel(excel_file, sheet_name='LabCourses', engine='openpyxl')
            
            return {
                'examiners': examiners_df,
                'lab_courses': lab_courses_df
            }
        except Exception as e:
            raise ValueError(
                f"Error reading Excel sheets: {str(e)}. "
                "Ensure 'Examiners' and 'LabCourses' sheets exist."
            )
    
    def _extract_teacher_names(self, dataframes: Dict[str, pd.DataFrame]) -> Set[str]:
        """Extract teacher names from both Examiners and LabCourses sheets."""
        all_teacher_names = set()
        
        examiners_df = dataframes['examiners']
        lab_courses_df = dataframes['lab_courses']
        
        # From Examiners sheet
        for col in ['1st Examiner', '2nd Examiner', '3rd Examiner', 'Question Typed By']:
            if col in examiners_df.columns:
                names = examiners_df[col].dropna().unique()
                all_teacher_names.update(names)
        
        # From LabCourses sheet
        for col in ['1st', '2nd', '3rd', '4th']:
            if col in lab_courses_df.columns:
                names = lab_courses_df[col].dropna().unique()
                all_teacher_names.update(names)
        
        return all_teacher_names
    
    def _extract_course_codes(self, dataframes: Dict[str, pd.DataFrame]) -> Set[str]:
        """Extract course codes from both sheets."""
        all_course_codes = set()
        
        examiners_df = dataframes['examiners']
        lab_courses_df = dataframes['lab_courses']
        
        # From Examiners sheet
        if 'Course' in examiners_df.columns:
            for course_str in examiners_df['Course'].dropna():
                course_code = self._extract_course_code_from_string(course_str)
                if course_code:
                    all_course_codes.add(course_code)
        
        # From LabCourses sheet
        if 'Lab Name' in lab_courses_df.columns:
            for course_str in lab_courses_df['Lab Name'].dropna():
                course_code = self._extract_course_code_from_string(course_str)
                if course_code:
                    all_course_codes.add(course_code)
        
        return all_course_codes
    
    def _process_remuneration_data(
        self, 
        dataframes: Dict[str, pd.DataFrame],
        teachers_data: Dict[str, Dict],
        teacher_map: Dict[str, Any],
        course_map: Dict[str, Any]
    ):
        """Process both Examiners and LabCourses data."""
        self._process_examiners_sheet(
            dataframes['examiners'], 
            teachers_data, 
            teacher_map
        )
        self._process_lab_courses_sheet(
            dataframes['lab_courses'], 
            teachers_data, 
            teacher_map
        )
    
    def _process_examiners_sheet(
        self, 
        examiners_df: pd.DataFrame,
        teachers_data: Dict[str, Dict],
        teacher_map: Dict[str, Any]
    ):
        """Process Examiners sheet data."""
        for idx, row in examiners_df.iterrows():
            course_str = row.get('Course')
            if pd.isna(course_str):
                continue
            
            course_code = self._extract_course_code_from_string(course_str)
            
            # Process 1st and 2nd Examiners
            self._process_first_second_examiners(row, course_code, teachers_data, teacher_map)
            
            # Process 3rd Examiner
            self._process_third_examiner(row, course_code, teachers_data, teacher_map)
            
            # Process Question Typed By
            self._process_question_typed_by(row, course_code, teachers_data, teacher_map)
    
    def _process_first_second_examiners(
        self, 
        row: pd.Series,
        course_code: str,
        teachers_data: Dict[str, Dict],
        teacher_map: Dict[str, Any]
    ):
        """Process 1st and 2nd examiners for question preparation and script evaluation."""
        for examiner_col in ['1st Examiner', '2nd Examiner']:
            examiner_name = row.get(examiner_col)
            if pd.notna(examiner_name) and examiner_name in teacher_map:
                teacher = teacher_map[examiner_name]
                script_count = self._safe_int_conversion(row.get('1st/2nd Examiner Count'))
                
                # Add Question Preparation
                teachers_data[teacher.id]["questionPreparations"].append({
                    "course_code": course_code,
                    "section_type": "Full"
                })
                
                # Add Script Evaluation
                if script_count > 0:
                    teachers_data[teacher.id]["scriptEvaluations"].append({
                        "course_code": course_code,
                        "script_type": "Final",
                        "script_count": script_count
                    })
    
    def _process_third_examiner(
        self, 
        row: pd.Series,
        course_code: str,
        teachers_data: Dict[str, Dict],
        teacher_map: Dict[str, Any]
    ):
        """Process 3rd examiner for answer sheet review."""
        examiner_3rd = row.get('3rd Examiner')
        if pd.notna(examiner_3rd) and examiner_3rd in teacher_map:
            teacher = teacher_map[examiner_3rd]
            answer_sheet_count = self._safe_int_conversion(row.get('3rd Examiner Count'))
            
            if answer_sheet_count > 0:
                teachers_data[teacher.id]["answerSheetReviews"].append({
                    "course_code": course_code,
                    "answer_sheet_count": answer_sheet_count
                })
    
    def _process_question_typed_by(
        self, 
        row: pd.Series,
        course_code: str,
        teachers_data: Dict[str, Dict],
        teacher_map: Dict[str, Any]
    ):
        """Process question typing for other remuneration."""
        typed_by = row.get('Question Typed By')
        if pd.notna(typed_by) and typed_by in teacher_map:
            teacher = teacher_map[typed_by]
            pages = self._safe_int_conversion(row.get('Pages in Question'))
            
            if pages > 0:
                teachers_data[teacher.id]["otherRemunerations"].append({
                    "remuneration_type": "Question Preparation and Printing",
                    "details": f"Question typing for {course_code}",
                    "page_count": pages
                })
    
    def _process_lab_courses_sheet(
        self, 
        lab_courses_df: pd.DataFrame,
        teachers_data: Dict[str, Dict],
        teacher_map: Dict[str, Any]
    ):
        """Process LabCourses sheet data."""
        for idx, row in lab_courses_df.iterrows():
            lab_name = row.get('Lab Name')
            if pd.isna(lab_name):
                continue
            
            course_code = self._extract_course_code_from_string(lab_name)
            student_count = self._safe_int_conversion(row.get('Total Students'))
            
            # Process all lab instructors
            for col in ['1st', '2nd', '3rd', '4th']:
                instructor_name = row.get(col)
                if pd.notna(instructor_name) and instructor_name in teacher_map:
                    teacher = teacher_map[instructor_name]
                    
                    teachers_data[teacher.id]["practicalExams"].append({
                        "course_code": course_code,
                        "student_count": student_count,
                        "day_count": 1
                    })

