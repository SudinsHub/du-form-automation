"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogAction,
  AlertDialogCancel
} from "@/components/ui/alert-dialog"

import DynamicSection from "./DynamicSection"

export default function RemunerationPresenter(props: any) {
  const {
    register,
    handleSubmit,
    onSubmit,
    years,
    handleYearChange,
    teachers,
    courses,
    selectedTeacher,
    selectedSemesterName,
    setSelectedSemesterName,
    loading,
    showExportDialog,
    setShowExportDialog,
    questionPreparations,
    setQuestionPreparations,
    questionModerations,
    setQuestionModerations,
    scriptEvaluations,
    setScriptEvaluations,
    practicalExams,
    setPracticalExams,
    vivaExams,
    setVivaExams,
    tabulations,
    setTabulations,
    answerSheetReviews,
    setAnswerSheetReviews,
    otherRemunerations,
    setOtherRemunerations,
    exportPDF,
    setValue
  } = props

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">

      {/* HEADER */}
      <Card>
        <CardHeader>
          <CardTitle>পরীক্ষক তথ্য</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

            {/* Teacher */}
            <div>
              <Label>পরীক্ষকের নাম</Label>
              <Select onValueChange={(v) => setValue("teacher_id", v)}>
                <SelectTrigger>
                  <SelectValue placeholder="পরীক্ষক নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {teachers.map(t => (
                    <SelectItem key={t.id} value={t.id.toString()}>
                      {t.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Semester */}
            <div>
              <Label>পরীক্ষার সেমিস্টার</Label>
              <Select onValueChange={setSelectedSemesterName}>
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

          {/* Teacher Card */}
          {selectedTeacher && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <p><strong>পদবী:</strong> {selectedTeacher.designation}</p>
              <p><strong>ঠিকানা:</strong> {selectedTeacher.department}, University of Dhaka</p>
            </div>
          )}

          {/* Year */}
          <div>
            <Select onValueChange={handleYearChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select Year" />
              </SelectTrigger>
              <SelectContent>
                {years.map(y => (
                  <SelectItem key={y} value={y.toString()}>
                    {y}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* REUSE EXISTING DynamicSection */}
      <DynamicSection
        title="(১) প্রশ্নপত্র প্রণয়ন"
        items={questionPreparations}
        setItems={setQuestionPreparations}
        courses={courses}
        renderFields={(item, i, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select onValueChange={(v) => updateItem(i, "course_code", Number(v))}>
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map(c => (
                    <SelectItem key={c.course_code} value={c.course_code}>
                      {c.course_code} - {c.course_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>পত্রের ধরণ</Label>
              <Select onValueChange={(v) => updateItem(i, "section_type", v)}>
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

      {/* Duplicate same pattern for other sections */}
      {/* (২) Moderation */}
      <DynamicSection
        title="(২) প্রশ্নপত্র সমন্বয় সাধন"
        items={questionModerations}
        setItems={setQuestionModerations}
        courses={courses}
        renderFields={(item, i, updateItem) => (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>কোর্স</Label>
              <Select onValueChange={(v) => updateItem(i, "course_code", Number(v))}>
                <SelectTrigger>
                  <SelectValue placeholder="কোর্স নির্বাচন করুন" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map(c => (
                    <SelectItem key={c.course_code} value={c.course_code}>
                      {c.course_code} - {c.course_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>প্রশ্ন সংখ্যা</Label>
              <input
                type="number"
                className="input"
                value={item.question_count}
                onChange={(e) => updateItem(i, "question_count", Number(e.target.value))}
              />
            </div>

            <div>
              <Label>সদস্য সংখ্যা</Label>
              <input
                type="number"
                className="input"
                value={item.team_member_count}
                onChange={(e) => updateItem(i, "team_member_count", Number(e.target.value))}
              />
            </div>
          </div>
        )}
      />

      {/* Continue same for other 5 sections... */}

      {/* Submit */}
      <Button type="submit" disabled={loading}>
        {loading ? "Submitting..." : "Submit"}
      </Button>

      {/* Export Dialog */}
      <AlertDialog open={showExportDialog} onOpenChange={setShowExportDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Export PDF?</AlertDialogTitle>
          </AlertDialogHeader>

          <AlertDialogFooter>
            <AlertDialogCancel>Close</AlertDialogCancel>
            <AlertDialogAction onClick={exportPDF}>Download</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </form>
  )
}
