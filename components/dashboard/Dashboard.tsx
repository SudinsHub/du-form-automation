"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { FileDown, Users, BookOpen } from "lucide-react"
import { semesterApi, reportApi, exportApi, type ExamSemester } from "@/services/api"

interface ReportData {
  teacher: {
    id: number
    name: string
    designation: string
    department: string
  }
  details: any
}

export default function Dashboard() {
  const [semesters, setSemesters] = useState<ExamSemester[]>([])
  const [selectedSemester, setSelectedSemester] = useState<number | null>(null)
  const [reportData, setReportData] = useState<ReportData[]>([])
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({
    totalTeachers: 0,
    totalSubmissions: 0,
  })

  useEffect(() => {
    loadSemesters()
  }, [])

  useEffect(() => {
    if (selectedSemester) {
      loadReport()
    }
  }, [selectedSemester])

  const loadSemesters = async () => {
    try {
      const response = await semesterApi.getAll()
      setSemesters(response.data)
    } catch (error) {
      console.error("Error loading semesters:", error)
    }
  }

  const loadReport = async () => {
    if (!selectedSemester) return

    setLoading(true)
    try {
      const response = await reportApi.getCumulativeReport(selectedSemester)
      setReportData(response.data)

      // Calculate stats
      const totalTeachers = response.data.length
      const totalSubmissions = response.data.length

      setStats({
        totalTeachers,
        totalSubmissions,
      })
    } catch (error) {
      console.error("Error loading report:", error)
    } finally {
      setLoading(false)
    }
  }

  const exportCumulativePDF = async () => {
    if (!selectedSemester) return

    try {
      const response = await exportApi.exportCumulativePDF({
        exam_semester_id: selectedSemester,
      })

      // Create download link
      const link = document.createElement("a")
      link.href = `data:application/pdf;base64,${response.data.pdf_data}`
      link.download = response.data.filename
      link.click()
    } catch (error) {
      console.error("Error exporting cumulative PDF:", error)
      alert("Error exporting PDF")
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("bn-BD", {
      style: "currency",
      currency: "BDT",
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const exportFormPDF = async (teacher_id:number, semester_id:number) => {
    try {
      const response = await exportApi.exportIndividualPDF({
        teacher_id: teacher_id,
        exam_semester_id: semester_id,
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">ড্যাশবোর্ড</h2>
        <div className="flex items-center space-x-4">
          <Select onValueChange={(value) => setSelectedSemester(Number(value))}>
            <SelectTrigger className="w-64">
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
          {selectedSemester && (
            <Button onClick={exportCumulativePDF}>
              <FileDown className="h-4 w-4 mr-2" />
              সামগ্রিক রিপোর্ট এক্সপোর্ট
            </Button>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      {selectedSemester && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">মোট শিক্ষক</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalTeachers}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">মোট জমা</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalSubmissions}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Report Table */}
      {selectedSemester && (
        <Card>
          <CardHeader>
            <CardTitle>রিপোর্ট</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">লোড হচ্ছে...</div>
            ) : reportData.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ক্রমিক নং</TableHead>
                    <TableHead>শিক্ষকের নাম ও ঠিকানা</TableHead>
                    <TableHead>পদবী</TableHead>
                    <TableHead>বিভাগ</TableHead>
                    <TableHead>ফর্ম ডাউনলোড</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {reportData.map((item, index) => (
                    <TableRow key={item.teacher.id}>
                      <TableCell>{index + 1}</TableCell>
                      <TableCell className="font-medium">{item.teacher.name}</TableCell>
                      <TableCell>{item.teacher.designation}</TableCell>
                      <TableCell>{item.teacher.department}</TableCell>
                      <TableCell> 
                          <FileDown className="h-6 w-6" onClick={() => { exportFormPDF(item.teacher.id, selectedSemester) }}/>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8 text-muted-foreground">কোন ডেটা পাওয়া যায়নি</div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
