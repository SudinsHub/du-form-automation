"use client"

import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
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

import RemunerationPresenter from "./RemunerationFormPresenter"

export interface FormData {
  teacher_id: string
  exam_semester_id: number
  exam_year: number
}

export default function RemunerationContainer() {
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 100 }, (_, i) => currentYear - i);

  // Global state
  const [selectedYear, setSelectedYear] = useState<number | null>(null)
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [selectedSemesterName, setSelectedSemesterName] = useState<string | null>(null)
  const [selectedTeacher, setSelectedTeacher] = useState<Teacher | null>(null)
  const [selectedSemester, setSelectedSemester] = useState<ExamSemester | null>(null)
  const [loading, setLoading] = useState(false)
  const [showExportDialog, setShowExportDialog] = useState(false)

  // Dynamic section states
  const [questionPreparations, setQuestionPreparations] = useState([{ course_code: "", section_type: "Full" }])
  const [questionModerations, setQuestionModerations] = useState([{ course_code: "", question_count: 0, team_member_count: 0 }])
  const [scriptEvaluations, setScriptEvaluations] = useState([{ course_code: "", script_type: "Final", script_count: 0 }])
  const [practicalExams, setPracticalExams] = useState([{ course_code: "", student_count: 0, day_count: 0 }])
  const [vivaExams, setVivaExams] = useState([{ course_code: "", student_count: 0 }])
  const [tabulations, setTabulations] = useState([{ course_code: "", student_count: 0 }])
  const [answerSheetReviews, setAnswerSheetReviews] = useState([{ course_code: "", answer_sheet_count: 0 }])
  const [otherRemunerations, setOtherRemunerations] = useState([
    { remuneration_type: "Exam Committee Honorium", details: "", page_count: 0 },
  ])

  // React Hook Form
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<FormData>()
  const watchedTeacherId = watch("teacher_id")

  const handleYearChange = (value: string) => {
    setSelectedYear(value ? Number(value) : null)
  }

  // Load semester dynamically
  useEffect(() => {
    loadSemester()
  }, [selectedSemesterName, selectedYear])

  const loadSemester = async () => {
    try {
      if (selectedSemesterName && selectedYear) {
        const response = await semesterApi.getOrCreate(selectedSemesterName, selectedYear)
        setSelectedSemester(response.data)
      }
    } catch (e) {
      alert("Semester load failed!")
    }
  }

  // Load teachers + courses initially
  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      const [tRes, cRes] = await Promise.all([teacherApi.getAll(), courseApi.getAll()])
      setTeachers(tRes.data)
      setCourses(cRes.data)
    } catch (e) {
      alert("Failed loading initial data!")
    }
  }

  // Select teacher info
  useEffect(() => {
    if (watchedTeacherId) {
      const teacher = teachers.find(t => t.id == watchedTeacherId)
      setSelectedTeacher(teacher || null)
    }
  }, [watchedTeacherId, teachers])

  // SUBMIT
  const onSubmit = async (data: FormData) => {
    if (!selectedTeacher || !selectedSemester) {
      alert("Select teacher & semester first.")
      return
    }

    setLoading(true)
    try {
      const payload: RemunerationSubmission = {
        teacher_id: data.teacher_id,
        exam_semester_id: selectedSemester.id,
        question_preparations: questionPreparations.filter(x => x.course_code !== ""),
        question_moderations: questionModerations.filter(x => x.course_code !== ""),
        script_evaluations: scriptEvaluations.filter(x => x.course_code !== ""),
        practical_exams: practicalExams.filter(x => x.course_code !== ""),
        viva_exams: vivaExams.filter(x => x.course_code !== ""),
        tabulations: tabulations.filter(x => x.course_code !== ""),
        answer_sheet_reviews: answerSheetReviews.filter(x => x.course_code !== ""),
        other_remunerations: otherRemunerations.filter(x => x.remuneration_type),
      }

      await remunerationApi.submit(payload)
      setShowExportDialog(true)
    } catch {
      alert("Submission failed.")
    }
    setLoading(false)
  }

  // EXPORT PDF
  const exportPDF = async () => {
    try {
      if (!selectedTeacher || !selectedSemester) return

      const res = await exportApi.exportIndividualPDF({
        teacher_id: selectedTeacher.id,
        exam_semester_id: selectedSemester.id,
      })

      const link = document.createElement("a")
      link.href = `data:application/pdf;base64,${res.data.pdf_data}`
      link.download = res.data.filename
      link.click()
    } catch {
      alert("Export failed")
    }
  }

  return (
    <RemunerationPresenter
      register={register}
      handleSubmit={handleSubmit}
      onSubmit={onSubmit}
      years={years}
      handleYearChange={handleYearChange}
      teachers={teachers}
      courses={courses}
      selectedTeacher={selectedTeacher}
      selectedSemesterName={selectedSemesterName}
      setSelectedSemesterName={setSelectedSemesterName}
      loading={loading}
      showExportDialog={showExportDialog}
      setShowExportDialog={setShowExportDialog}
      questionPreparations={questionPreparations}
      setQuestionPreparations={setQuestionPreparations}
      questionModerations={questionModerations}
      setQuestionModerations={setQuestionModerations}
      scriptEvaluations={scriptEvaluations}
      setScriptEvaluations={setScriptEvaluations}
      practicalExams={practicalExams}
      setPracticalExams={setPracticalExams}
      vivaExams={vivaExams}
      setVivaExams={setVivaExams}
      tabulations={tabulations}
      setTabulations={setTabulations}
      answerSheetReviews={answerSheetReviews}
      setAnswerSheetReviews={setAnswerSheetReviews}
      otherRemunerations={otherRemunerations}
      setOtherRemunerations={setOtherRemunerations}
      exportPDF={exportPDF}
      setValue={setValue}
    />
  )
}
