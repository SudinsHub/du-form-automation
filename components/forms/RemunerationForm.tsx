"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Save, FileDown } from "lucide-react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
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
import DynamicSection from "./DynamicSection"

interface FormData {
  teacher_id: number
  exam_semester_id: number
  exam_year: number
}

export default function RemunerationForm() {
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [semesters, setSemesters] = useState<ExamSemester[]>([])
  const [selectedTeacher, setSelectedTeacher] = useState<Teacher | null>(null)
  const [selectedSemester, setSelectedSemester] = useState<ExamSemester | null>(null)
  const [loading, setLoading] = useState(false)
  const [showExportDialog, setShowExportDialog] = useState(false)

  const [questionPreparations, setQuestionPreparations] = useState([{ course_id: 0, section_type: "Full" }])
  const [questionModerations, setQuestionModerations] = useState([
    { course_id: 0, question_count: 0, team_member_count: 0 },
  ])
  const [scriptEvaluations, setScriptEvaluations] = useState([{ course_id: 0, script_type: "Final", script_count: 0 }])
  const [practicalExams, setPracticalExams] = useState([{ course_id: 0, student_count: 0, day_count: 0 }])
  const [vivaExams, setVivaExams] = useState([{ course_id: 0, student_count: 0 }])
  const [tabulations, setTabulations] = useState([{ course_id: 0, student_count: 0 }])
  const [answerSheetReviews, setAnswerSheetReviews] = useState([{ course_id: 0, answer_sheet_count: 0 }])
  const [otherRemunerations, setOtherRemunerations] = useState([
    { remuneration_type: "Exam Committee Honorium", details: "", page_count: 0 },
  ])

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormData>()

  const watchedTeacherId = watch("teacher_id")
  const watchedSemesterId = watch("exam_semester_id")

  useEffect(() => {
    loadInitialData()
  }, [])

  useEffect(() => {
    if (watchedTeacherId) {
      const teacher = teachers.find((t) => t.id === Number(watchedTeacherId))
      setSelectedTeacher(teacher || null)
    }
  }, [watchedTeacherId, teachers])

  useEffect(() => {
    if (watchedSemesterId) {
      const semester = semesters.find((s) => s.id === Number(watchedSemesterId))
      setSelectedSemester(semester || null)
      if (semester) {
        setValue("exam_year", semester.year)
      }
    }
  }, [watchedSemesterId, semesters, setValue])

  const loadInitialData = async () => {
    try {
      const [teachersRes, coursesRes, semestersRes] = await Promise.all([
        teacherApi.getAll(),
        courseApi.getAll(),
        semesterApi.getAll(),
      ])
      setTeachers(teachersRes.data)
      setCourses(coursesRes.data)
      setSemesters(semestersRes.data)
    } catch (error) {
      console.error("Error loading initial data:", error)
    }
  }

  const onSubmit = async (data: FormData) => {
    if (!selectedTeacher || !selectedSemester) {
      alert("Please select teacher and semester")
      return
    }

    setLoading(true)
    try {
      const submissionData: RemunerationSubmission = {
        teacher_id: data.teacher_id,
        exam_semester_id: data.exam_semester_id,
        question_preparations: questionPreparations.filter((item) => item.course_id > 0),
        question_moderations: questionModerations.filter((item) => item.course_id > 0),
        script_evaluations: scriptEvaluations.filter((item) => item.course_id > 0),
        practical_exams: practicalExams.filter((item) => item.course_id > 0),
        viva_exams: vivaExams.filter((item) => item.course_id > 0),
        tabulations: tabulations.filter((item) => item.course_id > 0),
        answer_sheet_reviews: answerSheetReviews.filter((item) => item.course_id > 0),
        other_remunerations: otherRemunerations.filter((item) => item.remuneration_type && item.details),
      }

      await remunerationApi.submit(submissionData)
      setShowExportDialog(true)
    } catch (error) {
      console.error("Error submitting remuneration:", error)
      alert("Error submitting remuneration")
    } finally {
      setLoading(false)
    }
  }

  const exportPDF = async () => {
    if (!selectedTeacher || !selectedSemester) {
      alert("Please select teacher and semester")
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
      alert("Error exporting PDF")
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Header Information */}
      <Card>
        <CardHeader>
          <CardTitle>পরীক্ষক তথ্য</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="teacher_id">পরীক্ষকের নাম</Label>
              <Select onValueChange={(value) => setValue("teacher_id", Number(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="পরীক্ষক নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {teachers.map((teacher) => (
                    <SelectItem key={teacher.id} value={teacher.id.toString()}>
                      {teacher.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="exam_semester_id">পরীক্ষার সেমিস্টার</Label>
              <Select onValueChange={(value) => setValue("exam_semester_id", Number(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="সেমিস্টার নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {semesters.map((semester) => (
                    <SelectItem key={semester.id} value={semester.id.toString()}>
                      {semester.semester_name} - {semester.year}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {selectedTeacher && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <p>
                <strong>পদবী:</strong> {selectedTeacher.designation}
              </p>
              <p>
                <strong>ঠিকানা:</strong> {selectedTeacher.address}
              </p>
            </div>
          )}

          <div>
            <Label htmlFor="exam_year">পরীক্ষার বছর</Label>
            <Input
              {...register("exam_year", { required: true })}
              type="number"
              placeholder="২০২৩"
              readOnly={!!selectedSemester}
            />
          </div>
        </CardContent>
      </Card>

      {/* Question Preparation Section */}
      <DynamicSection
        title="(১) প্রশ্নপত্র প্রণয়ন"
        items={questionPreparations}
        setItems={setQuestionPreparations}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select onValueChange={(value) => updateItem(index, "course_id", Number(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id.toString()}>
                      {course.course_code} - {course.course_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>পত্রের ধরণ</Label>
              <Select onValueChange={(value) => updateItem(index, "section_type", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Full">পূর্ণপত্র</SelectItem>
                  <SelectItem value="Half">অর্ধপত্র</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )}
      />

      {/* Question Moderation Section */}
      <DynamicSection
        title="(২) প্রশ্নপত্র সমন্বয় সাধন"
        items={questionModerations}
        setItems={setQuestionModerations}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select onValueChange={(value) => updateItem(index, "course_id", Number(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id.toString()}>
                      {course.course_code} - {course.course_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>প্রশ্ন সংখ্যা</Label>
              <Input
                type="number"
                value={item.question_count}
                onChange={(e) => updateItem(index, "question_count", Number(e.target.value))}
                placeholder="০"
              />
            </div>
            <div>
              <Label>সদস্য সংখ্যা</Label>
              <Input
                type="number"
                value={item.team_member_count}
                onChange={(e) => updateItem(index, "team_member_count", Number(e.target.value))}
                placeholder="০"
              />
            </div>
          </div>
        )}
      />

      {/* Script Evaluation Section */}
      <DynamicSection
        title="(৩) উত্তরপত্র মূল্যায়ন করা"
        items={scriptEvaluations}
        setItems={setScriptEvaluations}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select onValueChange={(value) => updateItem(index, "course_id", Number(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id.toString()}>
                      {course.course_code} - {course.course_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>উত্তরপত্রের ধরণ</Label>
              <Select onValueChange={(value) => updateItem(index, "script_type", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Final">ফাইনাল</SelectItem>
                  <SelectItem value="Incourse">ইনকোর্স</SelectItem>
                  <SelectItem value="Assignment">অ্যাসাইনমেন্ট</SelectItem>
                  <SelectItem value="Presentation">প্রেজেন্টেশন</SelectItem>
                  <SelectItem value="Practical">ব্যবহারিক</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>খাতা সংখ্যা</Label>
              <Input
                type="number"
                value={item.script_count}
                onChange={(e) => updateItem(index, "script_count", Number(e.target.value))}
                placeholder="০"
              />
            </div>
          </div>
        )}
      />

      {/* Practical Exam Section */}
      <DynamicSection
        title="(৪) ব্যবহারিক পরীক্ষা"
        items={practicalExams}
        setItems={setPracticalExams}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select onValueChange={(value) => updateItem(index, "course_id", Number(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id.toString()}>
                      {course.course_code} - {course.course_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>শিক্ষার্থী সংখ্যা</Label>
              <Input
                type="number"
                value={item.student_count}
                onChange={(e) => updateItem(index, "student_count", Number(e.target.value))}
                placeholder="০"
              />
            </div>
            <div>
              <Label>দিন সংখ্যা</Label>
              <Input
                type="number"
                value={item.day_count}
                onChange={(e) => updateItem(index, "day_count", Number(e.target.value))}
                placeholder="০"
              />
            </div>
          </div>
        )}
      />

      {/* Viva Exam Section */}
      <DynamicSection
        title="(৫) মৌখিক পরীক্ষা"
        items={vivaExams}
        setItems={setVivaExams}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select onValueChange={(value) => updateItem(index, "course_id", Number(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id.toString()}>
                      {course.course_code} - {course.course_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>শিক্ষার্থী সংখ্যা</Label>
              <Input
                type="number"
                value={item.student_count}
                onChange={(e) => updateItem(index, "student_count", Number(e.target.value))}
                placeholder="০"
              />
            </div>
          </div>
        )}
      />

      {/* Tabulation Section */}
      <DynamicSection
        title="(৬) পরীক্ষার ফল সন্নিবেশকরণ"
        items={tabulations}
        setItems={setTabulations}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select onValueChange={(value) => updateItem(index, "course_id", Number(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id.toString()}>
                      {course.course_code} - {course.course_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>শিক্ষার্থী সংখ্যা</Label>
              <Input
                type="number"
                value={item.student_count}
                onChange={(e) => updateItem(index, "student_count", Number(e.target.value))}
                placeholder="০"
              />
            </div>
          </div>
        )}
      />

      {/* Answer Sheet Review Section */}
      <DynamicSection
        title="(৭) উত্তরপত্র নিরীক্ষা"
        items={answerSheetReviews}
        setItems={setAnswerSheetReviews}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select onValueChange={(value) => updateItem(index, "course_id", Number(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id.toString()}>
                      {course.course_code} - {course.course_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>উত্তরপত্র সংখ্যা</Label>
              <Input
                type="number"
                value={item.answer_sheet_count}
                onChange={(e) => updateItem(index, "answer_sheet_count", Number(e.target.value))}
                placeholder="০"
              />
            </div>
          </div>
        )}
      />

      {/* Other Remuneration Section */}
      <DynamicSection
        title="অন্যান্য"
        items={otherRemunerations}
        setItems={setOtherRemunerations}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>ধরণ</Label>
              <Select onValueChange={(value) => updateItem(index, "remuneration_type", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Exam Committee Honorium">পরীক্ষা কমিটি পদ</SelectItem>
                  <SelectItem value="Stencil">স্টেনসিল</SelectItem>
                  <SelectItem value="Question Setter">প্রশ্নকর্তা</SelectItem>
                  <SelectItem value="Question Preparation and Printing">প্রশ্নপত্র প্রস্তুতি ও মুদ্রণ</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>বিবরণ</Label>
              <Input
                value={item.details}
                onChange={(e) => updateItem(index, "details", e.target.value)}
                placeholder="বিস্তারিত লিখুন"
              />
            </div>
            <div>
              <Label>পৃষ্ঠা সংখ্যা (যদি প্রযোজ্য)</Label>
              <Input
                type="number"
                value={item.page_count || ""}
                onChange={(e) => updateItem(index, "page_count", Number(e.target.value))}
                placeholder="০"
              />
            </div>
          </div>
        )}
      />

      <Separator />

      {/* Action Buttons */}
      <div className="flex justify-end space-x-4">
        {/* <Button type="button" variant="outline" onClick={exportPDF}>
          <FileDown className="h-4 w-4 mr-2" />
          PDF এক্সপোর্ট করুন
        </Button> */}
        <Button type="submit" disabled={loading}>
          <Save className="h-4 w-4 mr-2" />
          {loading ? "সংরক্ষণ করা হচ্ছে..." : "সংরক্ষণ করুন"}
        </Button>
      </div>
      <AlertDialog open={showExportDialog} onOpenChange={setShowExportDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>ফর্ম সাবমিট সম্পন্ন হয়েছে</AlertDialogTitle>
            <AlertDialogDescription>
              আপনি কি এখনই ফর্মটি ডাউনলোড করতে চান?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>না</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                exportPDF()
                setShowExportDialog(false)
              }}
            >
              হ্যাঁ
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </form>
  )
}
