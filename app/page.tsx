"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import RemunerationForm from "@/components/forms/RemunerationForm"
import Dashboard from "@/components/dashboard/Dashboard"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { GraduationCap, FileText, BarChart3 } from "lucide-react"

export default function Home() {
  const [activeTab, setActiveTab] = useState("form")

  const initializeSampleData = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/init-data", {
        method: "POST",
      })
      if (response.ok) {
        alert("Sample data initialized successfully!")
      }
    } catch (error) {
      console.error("Error initializing sample data:", error)
      alert("Error initializing sample data")
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <GraduationCap className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ঢাকা বিশ্ববিদ্যালয়</h1>
                <p className="text-sm text-gray-600">পরীক্ষা সম্মানী ব্যবস্থাপনা সিস্টেম</p>
              </div>
            </div>
            <Button onClick={initializeSampleData} variant="outline">
              Initialize Sample Data
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="form" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>পরীক্ষা সম্মানী ফর্ম</span>
            </TabsTrigger>
            <TabsTrigger value="dashboard" className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>ড্যাশবোর্ড</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="form">
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">পরীক্ষা সম্মানী বিল ফর্ম</CardTitle>
              </CardHeader>
              <CardContent>
                <RemunerationForm />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="dashboard">
            <Dashboard />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
