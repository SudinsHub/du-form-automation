# Dhaka University Examination Remuneration System

A comprehensive web application for automating the examination remuneration bill process at Dhaka University.

## Features

- **Dynamic Form Interface**: Bangla interface matching the original paper form
- **PDF Generation**: Export individual bills and cumulative reports
- **Dashboard**: View statistics and manage submissions
- **Multi-section Support**: Handle all 7 main sections plus additional categories
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- SQLite (Database)
- WeasyPrint (PDF generation)
- Pydantic (Data validation)

### Frontend
- Next.js 14 (React framework)
- shadcn/ui (UI components)
- Tailwind CSS (Styling)
- Axios (HTTP client)
- React Hook Form (Form handling)

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
\`\`\`bash
cd backend
\`\`\`

2. Create a virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Run the FastAPI server:
\`\`\`bash
python main.py
\`\`\`

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Install Node.js dependencies:
\`\`\`bash
npm install
\`\`\`

2. Run the development server:
\`\`\`bash
npm run dev
\`\`\`

The frontend will be available at `http://localhost:3000`

### Initialize Sample Data

1. Open the application in your browser
2. Click the "Initialize Sample Data" button
3. This will create sample teachers, courses, and semesters

## Usage

### Creating a Remuneration Bill

1. Go to the "পরীক্ষা সংক্রান্ত সম্মানী ফর্ম" tab
2. Select a teacher from the dropdown
3. Select an exam semester
4. Fill in the relevant sections using the + and - buttons to add/remove subsections
5. Click "সংরক্ষণ করুন" to save
6. Click "PDF এক্সপোর্ট করুন" to download the filled form

### Viewing Reports

1. Go to the "ড্যাশবোর্ড" tab
2. Select a semester to view the cumulative report
3. Click "সামগ্রিক রিপোর্ট এক্সপোর্ট" to download the cumulative PDF

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Database Schema

The system uses the following main entities:
- Teachers
- Courses
- Exam Semesters
- Various remuneration categories (Question Preparation, Script Evaluation, etc.)
- Remuneration rates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
\`\`\`

This complete system provides:

1. **Full-stack application** with FastAPI backend and Next.js frontend
2. **Dynamic form handling** with add/remove sections
3. **PDF generation** for individual bills and cumulative reports
4. **Dashboard** with statistics and report management
5. **Bangla interface** matching the original form
6. **Sample data** for testing
7. **Responsive design** that works on all devices

To run the system:
1. Start the FastAPI backend: `python backend/main.py`
2. Start the Next.js frontend: `npm run dev`
3. Initialize sample data through the UI
4. Start creating remuneration bills!

The system handles all the requirements you specified, including the 7 main sections plus additional categories, PDF export functionality, and cumulative reporting.
