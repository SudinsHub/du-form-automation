'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { FileText, Calendar, DollarSign, FileDown } from "lucide-react";
import { exportApi } from "@/services/api";

interface SemesterRemuneration {
  semester: {
    id: number;
    name: string;
    year: number;
    exam_start_date: string | null;
    exam_end_date: string | null;
    result_publish_date: string | null;
  };
  remunerations: {
    question_preparations: any[];
    question_moderations: any[];
    script_evaluations: any[];
    practical_exams: any[];
    viva_exams: any[];
    tabulations: any[];
    answer_sheet_reviews: any[];
    other_remunerations: any[];
  };
}

export default function TeacherDashboard() {
  const [semesterRemunerations, setSemesterRemunerations] = useState<SemesterRemuneration[]>([]);
  const [loading, setLoading] = useState(true);
  const [teacherId, setTeacherId] = useState<string>("");

  useEffect(() => {
    loadTeacherProfile();
    loadRemunerations();
  }, []);

  const loadTeacherProfile = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/teacher/profile", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("auth-storage") ? JSON.parse(localStorage.getItem("auth-storage")!).state.token : ""}`,
        },
      });
      if (response.ok) {
        const teacher = await response.json();
        setTeacherId(teacher.id);
      }
    } catch (error) {
      console.error("Failed to load teacher profile:", error);
    }
  };

  const loadRemunerations = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/teacher/remuneration", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("auth-storage") ? JSON.parse(localStorage.getItem("auth-storage")!).state.token : ""}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setSemesterRemunerations(data);
      }
    } catch (error) {
      console.error("Failed to load remunerations:", error);
    } finally {
      setLoading(false);
    }
  };

  const exportFormPDF = async (semesterId: number) => {
    if (!teacherId) {
      alert("Teacher ID not available");
      return;
    }

    try {
      const response = await exportApi.exportIndividualPDF({
        teacher_id: teacherId,
        exam_semester_id: semesterId,
      });

      // Create download link
      const link = document.createElement("a");
      link.href = `data:application/pdf;base64,${response.data.pdf_data}`;
      link.download = response.data.filename;
      link.click();
    } catch (error) {
      console.error("Error exporting PDF:", error);
      alert("Error exporting PDF");
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <p>Loading...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            My Submitted Forms
          </CardTitle>
        </CardHeader>
        <CardContent>
          {semesterRemunerations.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No remuneration forms submitted yet.
            </p>
          ) : (
            <div className="space-y-6">
              {semesterRemunerations.map((item) => (
                <div key={item.semester.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-medium text-lg">
                        {item.semester.name} {item.semester.year}
                      </h3>
                      <p className="text-sm text-gray-500">
                        Exam Period: {item.semester.exam_start_date ? new Date(item.semester.exam_start_date).toLocaleDateString() : 'N/A'} - {item.semester.exam_end_date ? new Date(item.semester.exam_end_date).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="bg-blue-50 p-3 rounded">
                      <div className="font-medium text-blue-800">Question Prep</div>
                      <div className="text-blue-600">{item.remunerations.question_preparations.length} entries</div>
                    </div>
                    <div className="bg-green-50 p-3 rounded">
                      <div className="font-medium text-green-800">Script Eval</div>
                      <div className="text-green-600">{item.remunerations.script_evaluations.length} entries</div>
                    </div>
                    <div className="bg-purple-50 p-3 rounded">
                      <div className="font-medium text-purple-800">Practical</div>
                      <div className="text-purple-600">{item.remunerations.practical_exams.length} entries</div>
                    </div>
                    <div className="bg-orange-50 p-3 rounded">
                      <div className="font-medium text-orange-800">Other</div>
                      <div className="text-orange-600">{item.remunerations.other_remunerations.length} entries</div>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex justify-end">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => exportFormPDF(item.semester.id)}
                      className="flex items-center gap-2"
                    >
                      <FileDown className="h-4 w-4" />
                      Download PDF Report
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <Button className="w-full" onClick={() => window.location.href = "/teacher-remuneration-form"}>
            <FileText className="h-4 w-4 mr-2" />
            Submit New Remuneration Form
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}