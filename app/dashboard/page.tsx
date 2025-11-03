'use client';

import Dashboard from "@/components/dashboard/Dashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function DashboardPage() {
  return (
    <Card>
      <CardContent>
        <Dashboard />
      </CardContent>
    </Card>
  );
}
