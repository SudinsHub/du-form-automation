# University Form Automation

A web application for automating university remuneration forms with Excel import and PDF generation capabilities.

## Installation and Setup

### Prerequisites

- Node.js (for frontend)
- Python 3.8+ (for backend)
- npm (package manager)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Important: WeasyPrint Dependencies**

   **On Windows:**
   WeasyPrint requires GTK3 runtime. Download and install from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

   **On Linux:**
   ```bash
   sudo apt update
   sudo apt install -y \
     libcairo2 \
     libpango-1.0-0 \
     libpangocairo-1.0-0 \
     libgdk-pixbuf-2.0-0 \
     libharfbuzz0b \
     libfontconfig1 \
     libffi8
   ```

4. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

   The backend will run on http://localhost:8000

### Frontend Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will run on http://localhost:3000

## Test Data

- There's a test Excel file located at `files/4Y1S Bills - 2024 - Demo (2).xlsx`
- The database contains test data for 4th year 1st semester, 2024

## Test Credentials

### Super Admin

- username : superadmin
- password : password123

### Teacher 

- username : fahim_sir_csedu
- password : password123

## Usage

1. Start both backend and frontend servers
2. Access the application at http://localhost:3000
3. Use the Excel import feature to upload remuneration data
4. Generate PDF forms as needed