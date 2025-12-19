"use client"

import { useState, useEffect } from "react"
import {
  teacherApi,
  courseApi,
  semesterApi,
  remunerationApi,
  exportApi,
  type Teacher,
  type Course,
  type ExamSemester,
  type RemunerationSubmission,
} from "@/services/api"
import RemunerationFormPresenter from "./RemunerationFormPresenter"

// Define the form state interface
export interface RemunerationFormState {
  teacher_id: string
  exam_year: number
  teacher_name: string
  questionPreparations: Array<{ course_code: string; section_type: string }> // 1
  questionModerations: Array<{ course_code: string; question_count: number; team_member_count: number }> // 2
  scriptEvaluations: Array<{ course_code: string; script_type: string; script_count: number }> // 3
  practicalExams: Array<{ course_code: string; student_count: number; day_count: number }> // 4
  vivaExams: Array<{ course_code: string; student_count: number }> // 5
  tabulations: Array<{ course_code: string; student_count: number }>
  answerSheetReviews: Array<{ course_code: string; answer_sheet_count: number }> // 7
  otherRemunerations: Array<{ remuneration_type: string; details: string; page_count: number }>
}

export interface RemunerationFormContainerProps {
  // Optional prop for pre-filling data (when importing from Excel)
  initialData?: Partial<RemunerationFormState>
  // Optional teacher ID to pre-select
  preSelectedTeacherId?: string
  // Optional semester info to pre-select
  preSelectedSemester?: { name: string; year: number }
  // Callback when form is successfully saved
  onSaveSuccess?: () => void
}

export default function RemunerationFormContainer({
  initialData,
  preSelectedTeacherId,
  preSelectedSemester,
  onSaveSuccess,
}: RemunerationFormContainerProps) {
  const currentYear = new Date().getFullYear()

  // Master data states
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [selectedTeacher, setSelectedTeacher] = useState<Teacher | null>(null)
  const [selectedSemester, setSelectedSemester] = useState<ExamSemester | null>(null)
  const [selectedYear, setSelectedYear] = useState<number | null>(null)
  const [selectedSemesterName, setSelectedSemesterName] = useState<string | null>(null)

  // UI states
  const [loading, setLoading] = useState(false)
  const [showExportDialog, setShowExportDialog] = useState(false)

  // Form data states - initialized with defaults or pre-filled data
  const [formState, setFormState] = useState<RemunerationFormState>({
    teacher_id: preSelectedTeacherId || "",
    teacher_name: '',
    exam_year: currentYear,
    questionPreparations: initialData?.questionPreparations || [{ course_code: "", section_type: "Full" }],
    questionModerations: initialData?.questionModerations || [
      { course_code: "", question_count: 0, team_member_count: 0 },
    ],
    scriptEvaluations: initialData?.scriptEvaluations || [
      { course_code: "", script_type: "Final", script_count: 0 },
    ],
    practicalExams: initialData?.practicalExams || [{ course_code: "", student_count: 0, day_count: 0 }],
    vivaExams: initialData?.vivaExams || [{ course_code: "", student_count: 0 }],
    tabulations: initialData?.tabulations || [{ course_code: "", student_count: 0 }],
    answerSheetReviews: initialData?.answerSheetReviews || [{ course_code: "", answer_sheet_count: 0 }],
    otherRemunerations: initialData?.otherRemunerations || [
      { remuneration_type: "Exam Committee Honorium", details: "", page_count: 0 },
    ],
  })

  // Load initial master data (teachers, courses)
  useEffect(() => {
    loadInitialData()
  }, [])

  // Pre-select teacher if provided
  useEffect(() => {
    if (preSelectedTeacherId && teachers.length > 0) {
      const teacher = teachers.find((t) => t.id === preSelectedTeacherId)
      if (teacher) {
        setSelectedTeacher(teacher)
        setFormState((prev) => ({ ...prev, teacher_id: preSelectedTeacherId }))
      }
    }
  }, [preSelectedTeacherId, teachers])

  // Pre-select semester if provided
  useEffect(() => {
    if (preSelectedSemester) {
      setSelectedSemesterName(preSelectedSemester.name)
      setSelectedYear(preSelectedSemester.year)
    }
  }, [preSelectedSemester])

  // Load or create semester when name and year are selected
  useEffect(() => {
    loadSemester()
  }, [selectedSemesterName, selectedYear])

  // Update selected teacher when teacher_id changes
  useEffect(() => {
    if (formState.teacher_id && teachers.length > 0) {
      const teacher = teachers.find((t) => t.id === formState.teacher_id)
      setSelectedTeacher(teacher || null)
    }
  }, [formState.teacher_id, teachers])

  const loadInitialData = async () => {
    try {
      const [teachersRes, coursesRes] = await Promise.all([teacherApi.getAll(), courseApi.getAll()])
      setTeachers(teachersRes.data)
      setCourses(coursesRes.data)
    } catch (error) {
      console.error("Error loading initial data:", error)
      alert("মাস্টার ডেটা লোড করতে সমস্যা হয়েছে")
    }
  }

  const loadSemester = async () => {
    try {
      if (selectedSemesterName && selectedYear) {
        console.log(`Loading semester for ${selectedSemesterName} ${selectedYear}`)
        
        const response = await semesterApi.getOrCreate(selectedSemesterName, selectedYear)
        setSelectedSemester(response.data)
        setFormState((prev) => ({ ...prev, exam_semester_id: response.data.id }))
      }
    } catch (error: any) {
      console.error("Error loading semester:", error)
      alert("সেমিস্টার লোড করতে সমস্যা হয়েছে")
    }
  }

  const handleFormSubmit = async () => {
    if (!selectedTeacher || !selectedSemester) {
      alert("দয়া করে শিক্ষক এবং সেমিস্টার নির্বাচন করুন")
      return
    }

    setLoading(true)
    try {
      const submissionData: RemunerationSubmission = {
        teacher_id: formState.teacher_id,
        exam_semester_id: selectedSemester.id,
        question_preparations: formState.questionPreparations.filter((item) => item.course_code !== ""),
        question_moderations: formState.questionModerations.filter((item) => item.course_code !== ""),
        script_evaluations: formState.scriptEvaluations.filter((item) => item.course_code !== ""),
        practical_exams: formState.practicalExams.filter((item) => item.course_code !== ""),
        viva_exams: formState.vivaExams.filter((item) => item.course_code !== ""),
        tabulations: formState.tabulations.filter((item) => item.course_code !== ""),
        answer_sheet_reviews: formState.answerSheetReviews.filter((item) => item.course_code !== ""),
        other_remunerations: formState.otherRemunerations.filter(
          (item) => item.remuneration_type && item.details
        ),
      }

      await remunerationApi.submit(submissionData)
      setShowExportDialog(true)
      
      // Call success callback if provided
      if (onSaveSuccess) {
        onSaveSuccess()
      }
    } catch (error) {
      console.error("Error submitting remuneration:", error)
      alert("ফর্ম সাবমিট করতে সমস্যা হয়েছে")
    } finally {
      setLoading(false)
    }
  }

  const handleExportPDF = async () => {
    if (!selectedTeacher || !selectedSemester) {
      alert("দয়া করে শিক্ষক এবং সেমিস্টার নির্বাচন করুন")
      return
    }

    try {
      const response = await exportApi.exportIndividualPDF({
        teacher_id: selectedTeacher.id,
        exam_semester_id: selectedSemester.id,
      })

      // Create download link
      const link = document.createElement("a")
      link.href = `data:application/pdf;base64,${response.data.pdf_data}`
      link.download = response.data.filename
      link.click()
    } catch (error) {
      console.error("Error exporting PDF:", error)
      alert("PDF এক্সপোর্ট করতে সমস্যা হয়েছে")
    }
  }

  // Update form state helper
  const updateFormState = (updates: Partial<RemunerationFormState>) => {
    setFormState((prev) => ({ ...prev, ...updates }))
  }

  return (
    <RemunerationFormPresenter
      formState={formState}
      teachers={teachers}
      courses={courses}
      selectedTeacher={selectedTeacher}
      selectedSemester={selectedSemester}
      selectedYear={selectedYear}
      selectedSemesterName={selectedSemesterName}
      loading={loading}
      showExportDialog={showExportDialog}
      onFormStateUpdate={updateFormState}
      onTeacherChange={(teacherId) => updateFormState({ teacher_id: teacherId })}
      onSemesterNameChange={setSelectedSemesterName}
      onYearChange={setSelectedYear}
      onSubmit={handleFormSubmit}
      onExportPDF={handleExportPDF}
      onExportDialogChange={setShowExportDialog}
    />
  )
}