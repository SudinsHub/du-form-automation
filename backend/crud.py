from sqlalchemy.orm import Session
from sqlalchemy import and_
import models
import schemas
from typing import List

def get_teachers(db: Session):
    return db.query(models.Teacher).all()

def create_teacher(db: Session, teacher: schemas.TeacherCreate):
    db_teacher = models.Teacher(**teacher.dict())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

def get_courses(db: Session):
    return db.query(models.Course).all()

def create_course(db: Session, course: schemas.CourseCreate):
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_semesters(db: Session):
    return db.query(models.ExamSemester).all()

def create_semester(db: Session, semester: schemas.ExamSemesterCreate):
    db_semester = models.ExamSemester(**semester.dict())
    db.add(db_semester)
    db.commit()
    db.refresh(db_semester)
    return db_semester

def submit_remuneration(db: Session, data: schemas.RemunerationSubmission):
    # Delete existing records for this teacher and semester
    db.query(models.QuestionPreparation).filter(
        and_(models.QuestionPreparation.teacher_id == data.teacher_id,
             models.QuestionPreparation.exam_semester_id == data.exam_semester_id)
    ).delete()
    
    db.query(models.QuestionModeration).filter(
        and_(models.QuestionModeration.teacher_id == data.teacher_id,
             models.QuestionModeration.exam_semester_id == data.exam_semester_id)
    ).delete()
    
    db.query(models.ScriptEvaluation).filter(
        and_(models.ScriptEvaluation.teacher_id == data.teacher_id,
             models.ScriptEvaluation.exam_semester_id == data.exam_semester_id)
    ).delete()
    
    db.query(models.PracticalExam).filter(
        and_(models.PracticalExam.teacher_id == data.teacher_id,
             models.PracticalExam.exam_semester_id == data.exam_semester_id)
    ).delete()
    
    db.query(models.VivaExam).filter(
        and_(models.VivaExam.teacher_id == data.teacher_id,
             models.VivaExam.exam_semester_id == data.exam_semester_id)
    ).delete()
    
    db.query(models.Tabulation).filter(
        and_(models.Tabulation.teacher_id == data.teacher_id,
             models.Tabulation.exam_semester_id == data.exam_semester_id)
    ).delete()
    
    db.query(models.AnswerSheetReview).filter(
        and_(models.AnswerSheetReview.teacher_id == data.teacher_id,
             models.AnswerSheetReview.exam_semester_id == data.exam_semester_id)
    ).delete()
    
    db.query(models.OtherRemuneration).filter(
        and_(models.OtherRemuneration.teacher_id == data.teacher_id,
             models.OtherRemuneration.exam_semester_id == data.exam_semester_id)
    ).delete()
    
    # Insert new records
    for item in data.question_preparations:
        db_item = models.QuestionPreparation(
            teacher_id=data.teacher_id,
            exam_semester_id=data.exam_semester_id,
            **item.dict()
        )
        db.add(db_item)
    
    for item in data.question_moderations:
        db_item = models.QuestionModeration(
            teacher_id=data.teacher_id,
            exam_semester_id=data.exam_semester_id,
            **item.dict()
        )
        db.add(db_item)
    
    for item in data.script_evaluations:
        db_item = models.ScriptEvaluation(
            teacher_id=data.teacher_id,
            exam_semester_id=data.exam_semester_id,
            **item.dict()
        )
        db.add(db_item)
    
    for item in data.practical_exams:
        db_item = models.PracticalExam(
            teacher_id=data.teacher_id,
            exam_semester_id=data.exam_semester_id,
            **item.dict()
        )
        db.add(db_item)
    
    for item in data.viva_exams:
        db_item = models.VivaExam(
            teacher_id=data.teacher_id,
            exam_semester_id=data.exam_semester_id,
            **item.dict()
        )
        db.add(db_item)
    
    for item in data.tabulations:
        db_item = models.Tabulation(
            teacher_id=data.teacher_id,
            exam_semester_id=data.exam_semester_id,
            **item.dict()
        )
        db.add(db_item)
    
    for item in data.answer_sheet_reviews:
        db_item = models.AnswerSheetReview(
            teacher_id=data.teacher_id,
            exam_semester_id=data.exam_semester_id,
            **item.dict()
        )
        db.add(db_item)
    
    for item in data.other_remunerations:
        db_item = models.OtherRemuneration(
            teacher_id=data.teacher_id,
            exam_semester_id=data.exam_semester_id,
            **item.dict()
        )
        db.add(db_item)
    
    db.commit()
    return {"message": "Remuneration submitted successfully"}

def get_teacher_remuneration(db: Session, teacher_id: int, semester_id: int):
    result = {
        "question_preparations": db.query(models.QuestionPreparation).filter(
            and_(models.QuestionPreparation.teacher_id == teacher_id,
                 models.QuestionPreparation.exam_semester_id == semester_id)
        ).all(),
        "question_moderations": db.query(models.QuestionModeration).filter(
            and_(models.QuestionModeration.teacher_id == teacher_id,
                 models.QuestionModeration.exam_semester_id == semester_id)
        ).all(),
        "script_evaluations": db.query(models.ScriptEvaluation).filter(
            and_(models.ScriptEvaluation.teacher_id == teacher_id,
                 models.ScriptEvaluation.exam_semester_id == semester_id)
        ).all(),
        "practical_exams": db.query(models.PracticalExam).filter(
            and_(models.PracticalExam.teacher_id == teacher_id,
                 models.PracticalExam.exam_semester_id == semester_id)
        ).all(),
        "viva_exams": db.query(models.VivaExam).filter(
            and_(models.VivaExam.teacher_id == teacher_id,
                 models.VivaExam.exam_semester_id == semester_id)
        ).all(),
        "tabulations": db.query(models.Tabulation).filter(
            and_(models.Tabulation.teacher_id == teacher_id,
                 models.Tabulation.exam_semester_id == semester_id)
        ).all(),
        "answer_sheet_reviews": db.query(models.AnswerSheetReview).filter(
            and_(models.AnswerSheetReview.teacher_id == teacher_id,
                 models.AnswerSheetReview.exam_semester_id == semester_id)
        ).all(),
        "other_remunerations": db.query(models.OtherRemuneration).filter(
            and_(models.OtherRemuneration.teacher_id == teacher_id,
                 models.OtherRemuneration.exam_semester_id == semester_id)
        ).all(),
    }
    return result

def get_cumulative_report(db: Session, semester_id: int):
    # Get all teachers who have submitted for this semester
    teachers = db.query(models.Teacher).join(models.QuestionPreparation).filter(
        models.QuestionPreparation.exam_semester_id == semester_id
    ).distinct().all()
    
    report_data = []
    for teacher in teachers:
        teacher_data = get_teacher_remuneration(db, teacher.id, semester_id)
        
        report_data.append({
            "teacher": teacher,
            "details": teacher_data
        })
    
    return report_data
