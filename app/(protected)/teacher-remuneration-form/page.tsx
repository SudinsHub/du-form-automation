'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useState, useEffect } from "react";
import RemunerationFormContainer from "@/components/forms/RemunerationFormContainer";
import { useAuthStore } from "@/stores/useAuthStore";

export default function TeacherRemunerationFormPage() {
  const [teacherId, setTeacherId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTeacherProfile();
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
    } finally {
      setLoading(false);
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
    <Card>
      <CardHeader className="flex justify-between items-center">
        <CardTitle>পরীক্ষা সম্মানী বিল ফর্ম</CardTitle>
      </CardHeader>
      <CardContent>
        {teacherId ? (
          <RemunerationFormContainer preSelectedTeacherId={teacherId} />
        ) : (
          <p className="text-red-500">Failed to load teacher information.</p>
        )}
      </CardContent>
    </Card>
  );
}