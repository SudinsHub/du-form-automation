'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import RemunerationFormContainer from "@/components/forms/RemunerationFormContainer";
import { useRemunerationStore } from "@/stores/useRemunerationStore"

export default function FormPage() {
  const [loading, setLoading] = useState(false);
  // extract teacher_id from     window.open(`/remuneration/form?teacher_id=${encodeURIComponent(teacher_id)}`)
  const teacherId = typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('teacher_id') : null;
  const entry = teacherId ? useRemunerationStore(state => state.getEntry(teacherId)) : null;
  
  const initializeSampleData = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/api/v1/init-data", { method: "POST" });
      if (response.ok) alert("Sample data initialized successfully!");
    } catch (error) {
      alert("Error initializing sample data");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader className="flex justify-between items-center">
        <CardTitle>পরীক্ষা সম্মানী বিল ফর্ম</CardTitle>
        <Button onClick={initializeSampleData} variant="outline" disabled={loading}>
          {loading ? "Loading..." : "Initialize Sample Data"}
        </Button>
      </CardHeader>
      <CardContent>
        {entry ? (
          <RemunerationFormContainer
            initialData={entry.initialData}
            preSelectedTeacherId={entry.teacher_id}
            preSelectedSemester={{
              name: entry.semester_name,
              year: entry.exam_year,
            }}
          />
        ) : (
          <RemunerationFormContainer/>
        )}
      </CardContent>
    </Card>
  );
}
