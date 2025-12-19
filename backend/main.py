from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine, Base
import models
import schemas
from typing import List
import uvicorn
from contextlib import asynccontextmanager
from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session

# Import services
from services.teacher_service import TeacherService
from services.course_service import CourseService
from services.exam_semester_service import ExamSemesterService
from services.remuneration_service import RemunerationService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Debug: Print all registered tables
    print("Registered tables with Base:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")
    
    # Create tables on startup
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"Existing tables in database: {existing_tables}")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise
    
    yield

app = FastAPI(
    title="DU Examination Remuneration System", 
    version="2.0.0",
    description="Repository + Service Layer Pattern Implementation",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# TEACHERS ENDPOINTS
# ============================================
@app.get("/api/v1/teachers", response_model=List[schemas.Teacher])
def get_teachers(db: Session = Depends(get_db)):
    """Get all teachers"""
    try:
        service = TeacherService(db)
        return service.get_all_teachers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/teachers/{teacher_id}", response_model=schemas.Teacher)
def get_teacher(teacher_id: str, db: Session = Depends(get_db)):
    """Get a specific teacher by ID"""
    try:
        service = TeacherService(db)
        return service.get_teacher_by_id(teacher_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/teachers-by-name/{teacher_name}", response_model=schemas.Teacher)
def get_teacher(teacher_name: str, db: Session = Depends(get_db)):
    try:
        service = TeacherService(db)
        return service.get_teacher_by_name(teacher_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/teachers", response_model=schemas.Teacher, status_code=201)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    """Create a new teacher"""
    try:
        service = TeacherService(db)
        return service.create_teacher(teacher)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/teachers/department/{department}", response_model=List[schemas.Teacher])
def get_teachers_by_department(department: str, db: Session = Depends(get_db)):
    """Get all teachers in a specific department"""
    try:
        service = TeacherService(db)
        return service.get_teachers_by_department(department)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# COURSES ENDPOINTS
# ============================================
@app.get("/api/v1/courses", response_model=List[schemas.Course])
def get_courses(db: Session = Depends(get_db)):
    """Get all courses"""
    try:
        service = CourseService(db)
        return service.get_all_courses()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/courses/{course_code}", response_model=schemas.Course)
def get_course(course_code: str, db: Session = Depends(get_db)):
    """Get a specific course by code"""
    try:
        service = CourseService(db)
        return service.get_course_by_code(course_code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/courses", response_model=schemas.Course, status_code=201)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """Create a new course"""
    try:
        service = CourseService(db)
        return service.create_course(course)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/courses/department/{department}", response_model=List[schemas.Course])
def get_courses_by_department(department: str, db: Session = Depends(get_db)):
    """Get all courses for a specific department"""
    try:
        service = CourseService(db)
        return service.get_courses_by_department(department)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# EXAM SEMESTERS ENDPOINTS
# ============================================
@app.get("/api/v1/semesters", response_model=List[schemas.ExamSemester])
def get_semesters(db: Session = Depends(get_db)):
    """Get all exam semesters"""
    try:
        service = ExamSemesterService(db)
        return service.get_all_semesters()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/semesters/by-name-year", response_model=schemas.ExamSemester)
def get_semester_by_name_year(
    name: str = Query(...),
    year: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get semester by year and name"""
    try:
        service = ExamSemesterService(db)
        semester = service.get_semester_by_year_and_name(year, name)
        if not semester:
            raise HTTPException(status_code=404, detail="Semester not found")
        return semester
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/semesters/get-or-create", response_model=schemas.ExamSemester)
def get_or_create_semester(
    name: str = Query(...),
    year: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get existing semester or create new one"""
    try:
        service = ExamSemesterService(db)
        return service.get_or_create_semester(year, name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/semesters/{semester_id}", response_model=schemas.ExamSemester)
def get_semester(semester_id: int, db: Session = Depends(get_db)):
    """Get a specific semester by ID"""
    try:
        service = ExamSemesterService(db)
        return service.get_semester_by_id(semester_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/semesters", response_model=schemas.ExamSemester, status_code=201)
def create_semester(semester: schemas.ExamSemesterCreate, db: Session = Depends(get_db)):
    """Create a new semester"""
    try:
        service = ExamSemesterService(db)
        return service.create_semester(semester)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# REMUNERATION ENDPOINTS
# ============================================
@app.post("/api/v1/remuneration/submit", status_code=201)
def submit_remuneration(data: schemas.RemunerationSubmission, db: Session = Depends(get_db)):
    """Submit remuneration data for a teacher"""
    try:
        service = RemunerationService(db)
        return service.submit_remuneration(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/remuneration/teacher/{teacher_id}/semester/{semester_id}")
def get_teacher_remuneration(teacher_id: str, semester_id: int, db: Session = Depends(get_db)):
    """Get remuneration data for a specific teacher and semester"""
    try:
        service = RemunerationService(db)
        return service.get_teacher_remuneration(teacher_id, semester_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# REPORTS ENDPOINTS
# ============================================
@app.get("/api/v1/reports/cumulative/{semester_id}")
def get_cumulative_report(semester_id: int, db: Session = Depends(get_db)):
    """Generate cumulative report for a semester"""
    try:
        service = RemunerationService(db)
        return service.get_cumulative_report(semester_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# PDF EXPORT ENDPOINTS
# ============================================
@app.post("/api/v1/export/pdf/individual")
def export_individual_pdf(data: schemas.PDFExportRequest, db: Session = Depends(get_db)):
    """Export individual teacher remuneration as PDF"""
    try:
        from pdf_generator import generate_individual_pdf
        return generate_individual_pdf(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/export/pdf/cumulative")
def export_cumulative_pdf(data: schemas.CumulativeReportRequest, db: Session = Depends(get_db)):
    """Export cumulative report as PDF"""
    try:
        from pdf_generator import generate_cumulative_pdf
        return generate_cumulative_pdf(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# SEARCH ENDPOINTS
# ============================================
@app.get("/api/v1/search-teachers")
async def search_teachers(query: str, db: Session = Depends(get_db)):
    """Search for teachers from external source"""
    try:
        from utils.scrapper import teacher_parser
        from services.teacher_service import TeacherService
        
        found_teachers = await teacher_parser(query)
        teacher_service = TeacherService(db)
        
        for teacher_data in found_teachers:
            # Check if teacher exists using service layer
            teacher_exists = teacher_service.teacher_exists(teacher_data["code"])
            teacher_data["isNew"] = not teacher_exists

        return found_teachers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HEALTH CHECK
# ============================================
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}


@app.post("/api/remuneration/import-excel")
async def import_excel_remuneration(
    file: UploadFile = File(...),
    semester_name: str = Form(...),
    exam_year: int = Form(...),
    db: Session = Depends(get_db)
):
    service = RemunerationService(db)
    result = await service.process_excel_import(file, semester_name, exam_year)
    
    if result["code"] == 404:
        raise HTTPException(status_code=404, detail=result)
    
    return result

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)