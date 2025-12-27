'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, Search, Mail } from "lucide-react";
import { useState } from "react";
import { teacherApi, Teacher } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface ImportedTeacher {
  code: string;
  name: string;
  department: string;
  designation: string;
  isNew: boolean;
}

export default function ImportPage() {
    const [importedTeachers, setImportedTeachers] = useState<ImportedTeacher[]>([]);
    const [searchName, setSearchName] = useState<string>("");
    const [isFetching, setIsFetching] = useState<boolean>(false);
    const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
    const [selectedTeacherForInvite, setSelectedTeacherForInvite] = useState<ImportedTeacher | null>(null);
    const [inviteEmail, setInviteEmail] = useState("");
    const handleSearch = async () => {
        if (!searchName) return;
        try {
            setIsFetching(true);
            const response = await teacherApi.webImport({ name: searchName });
            setImportedTeachers(response.data);
            
        } catch (error) {
            console.error("Error importing teachers:", error);
            alert("Error importing teachers");
        } finally {
            setIsFetching(false);
        }
    };

    const handleSaveTeacher = async (code: string) => {
        const selectedTeacher = importedTeachers.find(t => t.code === code);
        if (!selectedTeacher) return;
        const newTeacher: Teacher = {
            id: code,
            name: selectedTeacher.name,
            department: selectedTeacher.department,
            designation: selectedTeacher.designation,
        };
        try {
            setIsFetching(true);
            const response = await teacherApi.create(newTeacher);
            alert("Teacher imported successfully");
        } catch (error) {
            console.error("Error saving teachers:", error);
            alert("Error saving teachers");
        } finally {
            setIsFetching(false);
        }
    };

    const handleInviteTeacher = async () => {
        if (!selectedTeacherForInvite || !inviteEmail) return;
        try {
            const response = await fetch(`http://localhost:8000/api/v1/teachers/${selectedTeacherForInvite.code}/invite`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("auth-storage") ? JSON.parse(localStorage.getItem("auth-storage")!).state.token : ""}`,
                },
                body: JSON.stringify({ teacher_id: selectedTeacherForInvite.code, email: inviteEmail }),
            });
            if (response.ok) {
                alert("Invitation sent successfully");
                setInviteDialogOpen(false);
                setInviteEmail("");
                setSelectedTeacherForInvite(null);
            } else {
                alert("Failed to send invitation");
            }
        } catch (error) {
            console.error("Error sending invitation:", error);
            alert("Error sending invitation");
        }
    };

  return (
    <Card>
      <CardHeader className="flex items-center gap-2">
        <Upload className="h-5 w-5 text-blue-600" />
        <CardTitle>Teacher Import</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="font-bold text-lg text-gray-800">Web Import</p>
        <form
        onSubmit={(e) => {
            e.preventDefault(); // prevent page reload
            handleSearch();
        }}
        className="flex px-2 mt-2 mb-4 text-gray-700"
        >
        <input
            type="text"
            className="mt-2 p-2 border border-gray-300 rounded-md w-full"
            placeholder="Search Name..."
            value={searchName}
            onChange={(e) => setSearchName(e.target.value)}
        />
        <button
            type="submit"
            className="mt-2 py-2 mx-4 bg-black text-white rounded-md hover:bg-gray-800 transition"
        >
            <Search className="h-4 w-12 inline-block mx-4" />
        </button>
        </form>

        {(importedTeachers.length > 0) && (
        <table className="w-full table-auto border-collapse border border-gray-300">
            <thead>
                <tr>
                    <th className="border border-gray-300 px-4 py-2">Code</th>
                    <th className="border border-gray-300 px-4 py-2">Name</th>
                    <th className="border border-gray-300 px-4 py-2">Department</th>
                    <th className="border border-gray-300 px-4 py-2">Designation</th>
                    <th className="border border-gray-300 px-4 py-2">Status</th>
                </tr>
            </thead>
            <tbody>
                {importedTeachers.map((teacher, index) => (
                    <tr key={index} className={teacher.isNew ? "bg-green-100" : ""}>
                        <td className="border border-gray-300 px-4 py-2">{teacher.code}</td>
                        <td className="border border-gray-300 px-4 py-2">{teacher.name}</td>
                        <td className="border border-gray-300 px-4 py-2">{teacher.department}</td>
                        <td className="border border-gray-300 px-4 py-2">{teacher.designation}</td>
                        <td className="border border-gray-300 px-4 py-2">{teacher.isNew ? 
                            <button
                                className="py-1 px-3 bg-black text-white rounded-md hover:bg-gray-800 transition"
                                onClick={() => handleSaveTeacher(teacher.code)}
                            >
                                Save
                            </button>
                        : 
                            <div className="flex gap-2">
                                <span className="text-gray-500">Existing</span>
                                <Dialog open={inviteDialogOpen && selectedTeacherForInvite?.code === teacher.code} onOpenChange={setInviteDialogOpen}>
                                    <DialogTrigger asChild>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => {
                                                setSelectedTeacherForInvite(teacher);
                                                setInviteDialogOpen(true);
                                            }}
                                        >
                                            <Mail className="h-4 w-4 mr-1" />
                                            Invite
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent>
                                        <DialogHeader>
                                            <DialogTitle>Invite Teacher</DialogTitle>
                                            <DialogDescription>
                                                Send an invitation email to {teacher.name} for account setup.
                                            </DialogDescription>
                                        </DialogHeader>
                                        <div className="grid gap-4 py-4">
                                            <div className="grid grid-cols-4 items-center gap-4">
                                                <Label htmlFor="email" className="text-right">
                                                    Email
                                                </Label>
                                                <Input
                                                    id="email"
                                                    value={inviteEmail}
                                                    onChange={(e) => setInviteEmail(e.target.value)}
                                                    className="col-span-3"
                                                    type="email"
                                                    placeholder="teacher@example.com"
                                                />
                                            </div>
                                        </div>
                                        <DialogFooter>
                                            <Button onClick={handleInviteTeacher}>Send Invitation</Button>
                                        </DialogFooter>
                                    </DialogContent>
                                </Dialog>
                            </div>
                        }</td>
                    </tr>
                ))}
            </tbody>
        </table>
        )}
        {isFetching && (
            <div className="flex items-center justify-center py-4">
                <p className="text-gray-500">Importing teachers...</p>
            </div>
        )}
      </CardContent>
    </Card>
  );
}
