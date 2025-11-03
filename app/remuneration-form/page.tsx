'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import RemunerationForm from "@/components/forms/RemunerationForm";

export default function FormPage() {
  const [loading, setLoading] = useState(false);

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
        <RemunerationForm />
      </CardContent>
    </Card>
  );
}
