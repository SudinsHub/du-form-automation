"use client"

import type { ReactNode } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus, Minus } from "lucide-react"
import type { Course } from "@/services/api"

interface DynamicSectionProps<T> {
  title: string
  items: T[]
  setItems: (items: T[]) => void
  courses: Course[]
  renderFields: (item: T, index: number, updateItem: (index: number, field: string, value: any) => void) => ReactNode
}

export default function DynamicSection<T extends Record<string, any>>({
  title,
  items,
  setItems,
  courses,
  renderFields,
}: DynamicSectionProps<T>) {
  const addItem = () => {
    const newItem = { ...items[0] } // Copy structure of first item
    // Reset all values to default
    Object.keys(newItem).forEach((key) => {
      if (typeof newItem[key] === "number") {
        newItem[key] = 0
      } else if (typeof newItem[key] === "string") {
        newItem[key] = ""
      }
    })
    setItems([...items, newItem])
  }

  const removeItem = (index: number) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index))
    }
  }

  const updateItem = (index: number, field: string, value: any) => {
    const updatedItems = [...items]
    updatedItems[index] = { ...updatedItems[index], [field]: value }
    setItems(updatedItems)
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>{title}</CardTitle>
          <div className="flex space-x-2">
            <Button type="button" variant="outline" size="sm" onClick={addItem}>
              <Plus className="h-4 w-4" />
            </Button>
            {items.length > 1 && (
              <Button type="button" variant="outline" size="sm" onClick={() => removeItem(items.length - 1)}>
                <Minus className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {items.map((item, index) => (
          <div key={index} className="p-4 border rounded-lg space-y-4">
            <div className="flex justify-between items-center">
              <span className="font-medium">উপধারা {index + 1}</span>
              {items.length > 1 && (
                <Button type="button" variant="ghost" size="sm" onClick={() => removeItem(index)}>
                  <Minus className="h-4 w-4" />
                </Button>
              )}
            </div>
            {renderFields(item, index, updateItem)}
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
