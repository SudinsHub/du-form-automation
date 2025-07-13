from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine, Base
import models  # This imports all models and registers them with Base
import crud
import schemas
from typing import List
import uvicorn
from contextlib import asynccontextmanager

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
    version="1.0.0",
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

# Teachers endpoints
@app.get("/api/v1/teachers", response_model=List[schemas.Teacher])
def get_teachers(db: Session = Depends(get_db)):
    return crud.get_teachers(db)

@app.post("/api/v1/teachers", response_model=schemas.Teacher)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    return crud.create_teacher(db, teacher)

# Courses endpoints
@app.get("/api/v1/courses", response_model=List[schemas.Course])
def get_courses(db: Session = Depends(get_db)):
    return crud.get_courses(db)

@app.post("/api/v1/courses", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    return crud.create_course(db, course)

# Exam Semesters endpoints
@app.get("/api/v1/semesters", response_model=List[schemas.ExamSemester])
def get_semesters(db: Session = Depends(get_db)):
    return crud.get_semesters(db)

@app.post("/api/v1/semesters", response_model=schemas.ExamSemester)
def create_semester(semester: schemas.ExamSemesterCreate, db: Session = Depends(get_db)):
    return crud.create_semester(db, semester)

# Remuneration submission
@app.post("/api/v1/remuneration/submit")
def submit_remuneration(data: schemas.RemunerationSubmission, db: Session = Depends(get_db)):
    return crud.submit_remuneration(db, data)

@app.get("/api/v1/remuneration/teacher/{teacher_id}/semester/{semester_id}")
def get_teacher_remuneration(teacher_id: int, semester_id: int, db: Session = Depends(get_db)):
    return crud.get_teacher_remuneration(db, teacher_id, semester_id)

# Reports endpoints
@app.get("/api/v1/reports/cumulative/{semester_id}")
def get_cumulative_report(semester_id: int, db: Session = Depends(get_db)):
    return crud.get_cumulative_report(db, semester_id)

# PDF Export endpoints
@app.post("/api/v1/export/pdf/individual")
def export_individual_pdf(data: schemas.PDFExportRequest, db: Session = Depends(get_db)):
    from pdf_generator import generate_individual_pdf
    return generate_individual_pdf(db, data)

@app.post("/api/v1/export/pdf/cumulative")
def export_cumulative_pdf(data: schemas.CumulativeReportRequest, db: Session = Depends(get_db)):
    from pdf_generator import generate_cumulative_pdf
    return generate_cumulative_pdf(db, data)

# Initialize sample data
@app.post("/api/v1/init-data")
def initialize_sample_data(db: Session = Depends(get_db)):
    # Verify tables exist before trying to use them
    from sqlalchemy import inspect
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"Tables available: {existing_tables}")
    
    if 'question_preparations' not in existing_tables:
        print("ERROR: question_preparations table not found!")
        print("Available tables:", existing_tables)
        print("Trying to create tables again...")
        
        # Try to create tables again
        Base.metadata.create_all(bind=engine)
        
        # Check again
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"Tables after recreation: {existing_tables}")
        
        if 'question_preparations' not in existing_tables:
            raise HTTPException(status_code=500, detail="Failed to create required tables")
    
    from sample_data import create_sample_data
    create_sample_data(db)
    return {"message": "Sample data created successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)