"use client"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Save } from "lucide-react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { type Teacher, type Course, type ExamSemester } from "@/services/api"
import DynamicSection from "./DynamicSection"
import type { RemunerationFormState } from "./RemunerationFormContainer"

interface RemunerationFormPresenterProps {
  formState: RemunerationFormState
  teachers: Teacher[]
  courses: Course[]
  selectedTeacher: Teacher | null
  selectedSemester: ExamSemester | null
  selectedYear: number | null
  selectedSemesterName: string | null
  loading: boolean
  showExportDialog: boolean
  onFormStateUpdate: (updates: Partial<RemunerationFormState>) => void
  onTeacherChange: (teacherId: string) => void
  onSemesterNameChange: (name: string) => void
  onYearChange: (year: number | null) => void
  onSubmit: () => void
  onExportPDF: () => void
  onExportDialogChange: (open: boolean) => void
}

export default function RemunerationFormPresenter({
  formState,
  teachers,
  courses,
  selectedTeacher,
  selectedSemester,
  selectedYear,
  selectedSemesterName,
  loading,
  showExportDialog,
  onFormStateUpdate,
  onTeacherChange,
  onSemesterNameChange,
  onYearChange,
  onSubmit,
  onExportPDF,
  onExportDialogChange,
}: RemunerationFormPresenterProps) {
  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 100 }, (_, i) => currentYear - i)
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    // This runs only on the client after initial render
    setIsMounted(true);
  }, [])
  const handleYearChange = (value: string) => {
    onYearChange(value ? parseInt(value) : null)
  }

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit()
  }

  return ( // render only after mounted to avoid hydration issues
    isMounted && (
    <form onSubmit={handleFormSubmit} className="space-y-6">
      {/* Header Information */}
      <Card>
        <CardHeader>
          <CardTitle>পরীক্ষক তথ্য</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="teacher_id">পরীক্ষকের নাম</Label>
              <Select 
                value={formState.teacher_id} 
                onValueChange={onTeacherChange}
              >
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
              <Select 
                value={selectedSemesterName || ""} 
                onValueChange={onSemesterNameChange}
              >
                <SelectTrigger>
                  <SelectValue placeholder="সেমিস্টার নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1st Year 1st Semester">১ম বর্ষ ১ম সেমিস্টার</SelectItem>
                  <SelectItem value="1st Year 2nd Semester">১ম বর্ষ ২য় সেমিস্টার</SelectItem>
                  <SelectItem value="2nd Year 1st Semester">২য় বর্ষ ১ম সেমিস্টার</SelectItem>
                  <SelectItem value="2nd Year 2nd Semester">২য় বর্ষ ২য় সেমিস্টার</SelectItem>
                  <SelectItem value="3rd Year 1st Semester">৩য় বর্ষ ১ম সেমিস্টার</SelectItem>
                  <SelectItem value="3rd Year 2nd Semester">৩য় বর্ষ ২য় সেমিস্টার</SelectItem>
                  <SelectItem value="4th Year 1st Semester">৪র্থ বর্ষ ১ম সেমিস্টার</SelectItem>
                  <SelectItem value="4th Year 2nd Semester">৪র্থ বর্ষ ২য় সেমিস্টার</SelectItem>
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
                <strong>ঠিকানা:</strong> {selectedTeacher.department}, University of Dhaka
              </p>
            </div>
          )}

          <div>
            <Label>পরীক্ষার বছর</Label>
            <Select value={selectedYear?.toString() || ""} onValueChange={handleYearChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="বছর নির্বাচন করুন" />
              </SelectTrigger>
              <SelectContent>
                {years.map((year) => (
                  <SelectItem key={year} value={year.toString()}>
                    {year}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Question Preparation Section */}
      <DynamicSection
        title="(১) প্রশ্নপত্র প্রণয়ন"
        items={formState.questionPreparations}
        setItems={(items) => onFormStateUpdate({ questionPreparations: items })}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select 
                value={item.course_code || ""} 
                onValueChange={(value) => updateItem(index, "course_code", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.course_code} value={course.course_code}>
                      {course.course_code} - {course.course_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>পত্রের ধরণ</Label>
              <Select 
                value={item.section_type || "Full"} 
                onValueChange={(value) => updateItem(index, "section_type", value)}
              >
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
        items={formState.questionModerations}
        setItems={(items) => onFormStateUpdate({ questionModerations: items })}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select 
                value={item.course_code || ""} 
                onValueChange={(value) => updateItem(index, "course_code", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.course_code} value={course.course_code}>
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
                value={item.question_count || 0}
                onChange={(e) => updateItem(index, "question_count", Number(e.target.value))}
                placeholder="০"
              />
            </div>
            <div>
              <Label>সদস্য সংখ্যা</Label>
              <Input
                type="number"
                value={item.team_member_count || 0}
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
        items={formState.scriptEvaluations}
        setItems={(items) => onFormStateUpdate({ scriptEvaluations: items })}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select 
                value={item.course_code || ""} 
                onValueChange={(value) => updateItem(index, "course_code", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.course_code} value={course.course_code}>
                      {course.course_code} - {course.course_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>উত্তরপত্রের ধরণ</Label>
              <Select 
                value={item.script_type || "Final"} 
                onValueChange={(value) => updateItem(index, "script_type", value)}
              >
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
                value={item.script_count || 0}
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
        items={formState.practicalExams}
        setItems={(items) => onFormStateUpdate({ practicalExams: items })}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select 
                value={item.course_code || ""} 
                onValueChange={(value) => updateItem(index, "course_code", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.course_code} value={course.course_code}>
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
                value={item.student_count || 0}
                onChange={(e) => updateItem(index, "student_count", Number(e.target.value))}
                placeholder="০"
              />
            </div>
            <div>
              <Label>দিন সংখ্যা</Label>
              <Input
                type="number"
                value={item.day_count || 0}
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
        items={formState.vivaExams}
        setItems={(items) => onFormStateUpdate({ vivaExams: items })}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select 
                value={item.course_code || ""} 
                onValueChange={(value) => updateItem(index, "course_code", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.course_code} value={course.course_code}>
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
                value={item.student_count || 0}
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
        items={formState.tabulations}
        setItems={(items) => onFormStateUpdate({ tabulations: items })}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select 
                value={item.course_code || ""} 
                onValueChange={(value) => updateItem(index, "course_code", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.course_code} value={course.course_code}>
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
                value={item.student_count || 0}
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
        items={formState.answerSheetReviews}
        setItems={(items) => onFormStateUpdate({ answerSheetReviews: items })}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select 
                value={item.course_code || ""} 
                onValueChange={(value) => updateItem(index, "course_code", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.course_code} value={course.course_code}>
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
                value={item.answer_sheet_count || 0}
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
        items={formState.otherRemunerations}
        setItems={(items) => onFormStateUpdate({ otherRemunerations: items })}
        courses={courses}
        renderFields={(item, index, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>ধরণ</Label>
              <Select 
                value={item.remuneration_type || ""} 
                onValueChange={(value) => updateItem(index, "remuneration_type", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Exam Committee Honorium">পরীক্ষা কমিটি পদ</SelectItem>
                  <SelectItem value="Stencil">স্টেনসিল</SelectItem>
                  <SelectItem value="Question Setter">প্রশ্নকর্তা</SelectItem>
                  <SelectItem value="Question Preparation and Printing">
                    প্রশ্নপত্র প্রস্তুতি ও মুদ্রণ
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>বিবরণ</Label>
              <Input
                value={item.details || ""}
                onChange={(e) => updateItem(index, "details", e.target.value)}
                placeholder="বিস্তারিত লিখুন"
              />
            </div>
            <div>
              <Label>পৃষ্ঠা সংখ্যা (যদি প্রযোজ্য)</Label>
              <Input
                type="number"
                value={item.page_count || 0}
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
        <Button type="submit" disabled={loading}>
          <Save className="h-4 w-4 mr-2" />
          {loading ? "সংরক্ষণ করা হচ্ছে..." : "সংরক্ষণ করুন"}
        </Button>
      </div>

      <AlertDialog open={showExportDialog} onOpenChange={onExportDialogChange}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>ফর্ম সাবমিট সম্পন্ন হয়েছে</AlertDialogTitle>
            <AlertDialogDescription>আপনি কি এখনই ফর্মটি ডাউনলোড করতে চান?</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>না</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                onExportPDF()
                onExportDialogChange(false)
              }}
            >
              হ্যাঁ
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </form>
  ))
}