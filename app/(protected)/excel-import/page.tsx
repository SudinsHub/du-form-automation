"use client"

import { useState } from 'react'
import { Dropzone, DropzoneEmptyState, DropzoneContent } from "@/components/ui/dropzone"
import { UploadIcon, CheckCircle, AlertCircle, ChevronLeft, ChevronRight, Save, X } from 'lucide-react'
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { useRouter } from 'next/navigation'
import { Separator } from "@/components/ui/separator"
import type { DropEvent, FileRejection } from 'react-dropzone'
import RemunerationFormContainer, { RemunerationFormState } from '@/components/forms/RemunerationFormContainer'
import { useRemunerationStore } from '@/stores/useRemunerationStore'



interface ImportResponse {
  status: string
  code: number
  message: string
  semester_name: string
  exam_year: number
  teachers_data: Partial<RemunerationFormState>[]
}

export default function ExcelImport() {
  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i)
  const addOrUpdateEntry = useRemunerationStore(state => state.addOrUpdateEntry)
  const baseUrl = 'http://localhost:8000'

  // Step 1: Upload configuration
  const [file, setFile] = useState<File | undefined>(undefined)
  const [selectedSemester, setSelectedSemester] = useState<string>("")
  const [selectedYear, setSelectedYear] = useState<number | undefined>(undefined)
  
  // Step 2: Review state
  const [importResponse, setImportResponse] = useState<ImportResponse | null>(null)
  const [currentTeacherIndex, setCurrentTeacherIndex] = useState(0)
  const [teachersData, setTeachersData] = useState<Partial<RemunerationFormState>[]>([])
  
  // UI states
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)


  const handleDrop = (acceptedFiles: File[], fileRejections: FileRejection[], event: DropEvent) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0])
      setUploadError(null)
    }
  }
  const handleTeacherCardClick = (teacher_id: string, teacher_data: Partial<RemunerationFormState>, semester: string, exam_year: number) => {
      addOrUpdateEntry(
      teacher_id,
      teacher_data,
      semester,
      exam_year
    )
    // Navigate to the remuneration form page for this teacher in a new tab
    window.open(`/remuneration-form?teacher_id=${encodeURIComponent(teacher_id)}`)

  }
  const handleSubmit = async () => {
    if (!file || !selectedSemester || !selectedYear) {
      setUploadError("দয়া করে সেমিস্টার, বছর এবং ফাইল নির্বাচন করুন")
      return
    }

    setIsUploading(true)
    setUploadError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('semester_name', selectedSemester)
      formData.append('exam_year', selectedYear.toString())

      const response = await fetch(`${baseUrl}/api/remuneration/import-excel`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || 'Upload failed')
      }

      const data: ImportResponse = await response.json()
      setImportResponse(data)
      setTeachersData(data.teachers_data)
      setCurrentTeacherIndex(0)
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'আপলোড ব্যর্থ হয়েছে')
      console.log("Error:", error);
      
    } finally {
      setIsUploading(false)
    }
  }

  if(importResponse && teachersData.length > 0) {
    return ( // Review each teacher's data to a card, clicking on that card will open the RemunerationFormContainer with that data loaded
      // Recommended Structure using Tailwind/shadcn components
      <div>
        <h2 className="text-2xl font-semibold mb-4">
          আপলোড করা ফাইলে নিম্নলিখিত শিক্ষকগণ পাওয়া গেছে:
        </h2>
        {teachersData.map((teacherData, index) => (
          <Card 
            // Add a slight shadow and transition for a better hover effect
            key={index}
            className="mb-4 shadow-sm hover:shadow-md transition-shadow duration-200"
          >
            
            {/* Use CardHeader to contain the main elements, 
              making it flexible to space the Title and Button.
            */}
            <CardHeader className="flex flex-row items-center justify-between p-4 sm:p-6">
              
              {/* Left Side: Teacher Name and optional Subtitle */}
              <div>
                <CardTitle className="text-lg font-semibold text-gray-800">
                  {/* Fallback to a placeholder if the name is missing */}
                  {teacherData.teacher_name || 'অজানা পরীক্ষক'}
                </CardTitle>

              </div>

              {/* Right Side: Manage Button */}
              <Button
                // Use a more prominent variant like 'default' or 'secondary' if appropriate
                variant="default" 
                size="sm"
                onClick={() => handleTeacherCardClick(
                  teacherData.teacher_id || '',
                  teacherData,
                  importResponse.semester_name,
                  importResponse.exam_year
                )}
              >
                {/* Add an icon (if you have one like Lucide React's Settings or Edit) */}
                Manage
              </Button>
            </CardHeader>
            
          </Card>
        ))} 
      </div>

    )


  }



  // Upload form
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>এক্সেল থেকে</CardTitle>
          <CardDescription>সেমিস্টার এবং বছর নির্বাচন করুন, তারপর এক্সেল ফাইল আপলোড করুন</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {uploadError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{uploadError}</AlertDescription>
            </Alert>
          )}

          <div>
            <Label htmlFor="exam_semester">পরীক্ষার সেমিস্টার</Label>
            <Select value={selectedSemester} onValueChange={setSelectedSemester}>
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

          <div>
            <Label>পরীক্ষার বছর</Label>
            <Select value={selectedYear?.toString() || ""} onValueChange={(val) => setSelectedYear(parseInt(val))}>
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

          <Separator />

          <div>
            <Label>এক্সেল আপলোড করুন</Label>
            <Dropzone 
              onDrop={handleDrop} 
              onError={console.error} 
              src={file} 
              accept={{ 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx', '.xls'] }}
            >
              <DropzoneEmptyState>
                <div className="flex w-full items-center gap-4 p-8">
                  <div className="flex size-16 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                    <UploadIcon size={24} />
                  </div>
                  <div className="text-left">
                    <p className="font-medium text-sm">এক্সেল ফাইল আপলোড করুন</p>
                    <p className="text-muted-foreground text-xs">
                      ড্র্যাগ করুন অথবা ক্লিক করুন (.xlsx, .xls)
                    </p>
                  </div>
                </div>
              </DropzoneEmptyState>
            </Dropzone>
            {file && (
              <div className="mt-2 text-sm text-gray-600">
                নির্বাচিত ফাইল: {file.name}
              </div>
            )}
          </div>

          <Button 
            onClick={handleSubmit} 
            disabled={!file || !selectedSemester || !selectedYear || isUploading}
            className="w-full"
          >
            {isUploading ? 'আপলোড হচ্ছে...' : 'এক্সেল আপলোড করুন'}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}