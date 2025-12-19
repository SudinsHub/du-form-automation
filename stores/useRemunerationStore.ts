// stores/useRemunerationStore.ts
import { create } from "zustand"
import { persist } from "zustand/middleware"
import { RemunerationFormState } from "@/components/forms/RemunerationFormContainer"

interface TeacherRemunerationEntry {
  teacher_id: string
  initialData: Partial<RemunerationFormState>
  semester_name: string
  exam_year: number
}

interface RemunerationStore {
  entries: Record<string, TeacherRemunerationEntry>

  addOrUpdateEntry: (
    teacherId: string,
    data: Partial<RemunerationFormState>,
    semester: string,
    year: number
  ) => void

  getEntry: (teacherId: string) => TeacherRemunerationEntry | null

  removeEntry: (teacherId: string) => void

  clearAll: () => void
}

export const useRemunerationStore = create<RemunerationStore>()(
  persist(
    (set, get) => ({
      entries: {},

      addOrUpdateEntry: (teacherId, data, semester, year) =>
        set((state) => ({
          entries: {
            ...state.entries,
            [teacherId]: {
              teacher_id: teacherId,
              initialData: data,
              semester_name: semester,
              exam_year: year,
            },
          },
        })),

      getEntry: (teacherId) => get().entries[teacherId] ?? null,

      removeEntry: (teacherId) =>
        set((state) => {
          const updated = { ...state.entries }
          delete updated[teacherId]
          return { entries: updated }
        }),

      clearAll: () => set({ entries: {} }),
    }),
    {
      name: "remuneration-store", // Key in localStorage
      version: 1,
    }
  )
)
