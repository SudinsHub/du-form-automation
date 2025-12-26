import axios from "axios"
import { useAuthStore } from "@/stores/useAuthStore";

const API_BASE_URL = "http://localhost:8000/api/v1"

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);


export interface Teacher {
  id: string
  name: string
  designation: string
  department: string
  mobile_no?: string
}

export interface Course {
  course_code: string
  course_title: string
  credits: number
  department: string
}

export interface ExamSemester {
  id: number
  year: number
  semester_name: string
  exam_start_date?: string
  exam_end_date?: string
  result_publish_date?: string
  chairman_id: number
}

export interface RemunerationSubmission {
  teacher_id: string
  exam_semester_id: number
  question_preparations: QuestionPreparationData[]
  question_moderations: QuestionModerationData[]
  script_evaluations: ScriptEvaluationData[]
  practical_exams: PracticalExamData[]
  viva_exams: VivaExamData[]
  tabulations: TabulationData[]
  answer_sheet_reviews: AnswerSheetReviewData[]
  other_remunerations: OtherRemunerationData[]
}

export interface QuestionPreparationData {
  course_code: string
  section_type: string
}

export interface QuestionModerationData {
  course_code: string
  question_count: number
  team_member_count: number
}

export interface ScriptEvaluationData {
  course_code: string
  script_type: string
  script_count: number
}

export interface PracticalExamData {
  course_code: string
  student_count: number
  day_count: number
}

export interface VivaExamData {
  course_code: string
  student_count: number
}

export interface TabulationData {
  course_code: string
  student_count: number
}

export interface AnswerSheetReviewData {
  course_code: string
  answer_sheet_count: number
}

export interface OtherRemunerationData {
  remuneration_type: string
  details: string
  page_count?: number
}



// API functions
export const teacherApi = {
  getAll: () => api.get<Teacher[]>("/teachers"),
  create: (data: Teacher) => api.post<Teacher>("/teachers", data),
  webImport: (data: { name: string }) => api.get(`/search-teachers?query=${encodeURIComponent(data.name)}`),

}

export const courseApi = {
  getAll: () => api.get<Course[]>("/courses"),
  create: (data: Omit<Course, "id">) => api.post<Course>("/courses", data),
}

export const semesterApi = {
  getAll: () => api.get<ExamSemester[]>("/semesters"),
  create: (data: Omit<ExamSemester, "id">) => api.post<ExamSemester>("/semesters", data),
  getByNameAndYear: (name: string, year: number) => 
    api.get<ExamSemester>(`/semesters/by-name-year?name=${encodeURIComponent(name)}&year=${year}`),
  getOrCreate: async (name: string, year: number) => api.get<ExamSemester>(`/semesters/get-or-create?name=${encodeURIComponent(name)}&year=${year}`),
}

export const remunerationApi = {
  submit: (data: RemunerationSubmission) => api.post("/remuneration/submit", data),
  getTeacherRemuneration: (teacherId: number, semesterId: number) =>
    api.get(`/remuneration/teacher/${teacherId}/semester/${semesterId}`),
}

export const reportApi = {
  getCumulativeReport: (semesterId: number) => api.get(`/reports/cumulative/${semesterId}`),
}

export const exportApi = {
  exportIndividualPDF: (data: { teacher_id: string; exam_semester_id: number }) =>
    api.post("/export/pdf/individual", data),
  exportCumulativePDF: (data: { exam_semester_id: number }) => api.post("/export/pdf/cumulative", data),
}

export default api
