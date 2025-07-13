from sqlalchemy.orm import Session
import models
from datetime import date

def create_sample_data(db: Session):
    # Clear existing data
    db.query(models.QuestionPreparation).delete()
    db.query(models.QuestionModeration).delete()
    db.query(models.ScriptEvaluation).delete()
    db.query(models.PracticalExam).delete()
    db.query(models.VivaExam).delete()
    db.query(models.Tabulation).delete()
    db.query(models.AnswerSheetReview).delete()
    db.query(models.OtherRemuneration).delete()
    db.query(models.Course).delete()
    db.query(models.ExamSemester).delete()
    db.query(models.Teacher).delete()
    
    # Create teachers
    teachers = [
        models.Teacher(
            name="Dr. Shabbir Ahmed",
            designation="Professor",
            department="CSE",
            address="Department of CSE, University of Dhaka",
            mobile_no="+880 1726784520"
        ),
        models.Teacher(
            name="Dr. Ismat Rahman",
            designation="Professor",
            department="CSE",
            address="Department of CSE, University of Dhaka",
            mobile_no="+880 1712345678"
        ),
        models.Teacher(
            name="Md Mahmudur Rahman",
            designation="Associate Professor",
            department="CSE",
            address="Department of CSE, University of Dhaka",
            mobile_no="+880 1798765432"
        ),
        models.Teacher(
            name="Dr. Md. Shafiul Alam",
            designation="Assistant Professor",
            department="CSE",
            address="Department of CSE, University of Dhaka",
            mobile_no="+880 1756789012"
        ),
        models.Teacher(
            name="Dr. Md. Rezaul Karim",
            designation="Professor",
            department="CSE",
            address="Department of CSE, University of Dhaka",
            mobile_no="+880 1734567890"
        )
    ]
    
    for teacher in teachers:
        db.add(teacher)
    db.commit()
    
    # Create courses
    courses = [
        models.Course(course_code="CSE-2201", course_title="Database Management Systems-I", credits=3.0, department="CSE"),
        models.Course(course_code="CSE-2202", course_title="Design and Analysis of Algorithms-I", credits=3.0, department="CSE"),
        models.Course(course_code="CSE-2203", course_title="Data and Telecommunications", credits=3.0, department="CSE"),
        models.Course(course_code="CSE-2204", course_title="Computer Architecture and Organization", credits=3.0, department="CSE"),
        models.Course(course_code="CSE-2205", course_title="Introduction to Mechatronics", credits=2.0, department="CSE"),
        models.Course(course_code="CSE-2211", course_title="Database Management Systems-I Lab", credits=1.5, department="CSE"),
        models.Course(course_code="CSE-2212", course_title="Design and Analysis of Algorithms-I Lab", credits=1.5, department="CSE"),
        models.Course(course_code="CSE-2213", course_title="Data and Telecommunication Lab", credits=0.75, department="CSE"),
        models.Course(course_code="CSE-2216", course_title="Application Development Lab", credits=1.5, department="CSE")
    ]
    
    for course in courses:
        db.add(course)
    db.commit()
    
    # Create exam semester
    semester = models.ExamSemester(
        year=2023,
        semester_name="2nd Year 2nd Semester",
        exam_start_date=date(2025, 2, 11),
        exam_end_date=date(2025, 2, 27),
        result_publish_date=date(2025, 3, 15),
        chairman_id=1  # Dr. Shabbir Ahmed
    )
    db.add(semester)
    db.commit()
    
    print("Sample data created successfully!")
