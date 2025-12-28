'use client'

import { useState, useMemo, useEffect } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
} from '@tanstack/react-table'
import { weeklyReportAPI } from '@/lib/api'

interface ReportRow {
  day_of_week: string
  period_index: number
  subject_name: string
  lesson_name: string
  notes: string
}

interface WeeklyReportTableProps {
  data: ReportRow[]
  weekNumber: number
  onSave: (logs: any[]) => void
  subjects?: string[]
}

const columnHelper = createColumnHelper<ReportRow>()

export function WeeklyReportTable({ data, weekNumber, onSave, subjects = [] }: WeeklyReportTableProps) {
  const [editableData, setEditableData] = useState<ReportRow[]>(data || [])
  const [editingCell, setEditingCell] = useState<{ row: number; col: string } | null>(null)
  const [showLessonsSidebar, setShowLessonsSidebar] = useState(false)
  const [selectedSubjectForLessons, setSelectedSubjectForLessons] = useState<string>('')
  const [lessons, setLessons] = useState<Array<{ lesson_index: number; lesson_name: string }>>([])

  useEffect(() => {
    setEditableData(data)
  }, [data])

  const dayMapping: { [key: string]: number } = {
    'Thứ 2': 2,
    'Thứ 3': 3,
    'Thứ 4': 4,
    'Thứ 5': 5,
    'Thứ 6': 6,
  }

  const columns = useMemo(
    () => [
      columnHelper.accessor('day_of_week', {
        header: 'Thứ',
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor('period_index', {
        header: 'Tiết',
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor('subject_name', {
        header: 'Môn học',
        cell: (info) => {
          const rowIndex = info.row.index
          const isEditing = editingCell?.row === rowIndex && editingCell?.col === 'subject_name'
          const value = editableData[rowIndex]?.subject_name || ''

          if (isEditing) {
            return (
              <select
                value={value}
                onChange={(e) => {
                  const newData = [...editableData]
                  newData[rowIndex] = { ...newData[rowIndex], subject_name: e.target.value }
                  setEditableData(newData)
                }}
                onBlur={() => setEditingCell(null)}
                className="w-full px-2 py-1 border rounded bg-white"
                autoFocus
                onClick={(e) => e.stopPropagation()}
              >
                <option value="">-- Chọn môn --</option>
                {subjects && subjects.length > 0 ? (
                  subjects.map((subject) => (
                    <option key={subject} value={subject}>
                      {subject}
                    </option>
                  ))
                ) : null}
              </select>
            )
          }
          return (
            <div
              onClick={() => setEditingCell({ row: rowIndex, col: 'subject_name' })}
              className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded"
            >
              {value || <span className="text-gray-400">Click để chọn</span>}
            </div>
          )
        },
      }),
      columnHelper.accessor('lesson_name', {
        header: 'Tên bài dạy',
        cell: (info) => {
          const rowIndex = info.row.index
          const isEditing = editingCell?.row === rowIndex && editingCell?.col === 'lesson_name'
          const value = editableData[rowIndex]?.lesson_name || ''
          const subjectName = editableData[rowIndex]?.subject_name || ''

          if (isEditing) {
            return (
              <input
                type="text"
                value={value}
                onChange={(e) => {
                  const newData = [...editableData]
                  newData[rowIndex] = { ...newData[rowIndex], lesson_name: e.target.value }
                  setEditableData(newData)
                }}
                onFocus={async () => {
                  // Khi focus vào input, load danh sách tiết học nếu có môn học
                  if (subjectName) {
                    try {
                      const response = await weeklyReportAPI.getLessonsBySubject(subjectName)
                      setLessons(response.lessons || [])
                      setSelectedSubjectForLessons(subjectName)
                      setShowLessonsSidebar(true)
                    } catch (err) {
                      console.error('Error loading lessons:', err)
                    }
                  }
                }}
                onBlur={() => {
                  // Delay để cho phép click vào sidebar
                  setTimeout(() => setEditingCell(null), 200)
                }}
                className="w-full px-2 py-1 border rounded"
                autoFocus
              />
            )
          }
          return (
            <div
              onClick={async () => {
                setEditingCell({ row: rowIndex, col: 'lesson_name' })
                // Load danh sách tiết học khi click
                if (subjectName) {
                  try {
                    const response = await weeklyReportAPI.getLessonsBySubject(subjectName)
                    setLessons(response.lessons || [])
                    setSelectedSubjectForLessons(subjectName)
                    setShowLessonsSidebar(true)
                  } catch (err) {
                    console.error('Error loading lessons:', err)
                  }
                }
              }}
              className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded"
            >
              {value || <span className="text-gray-400">Click để điền</span>}
            </div>
          )
        },
      }),
      columnHelper.accessor('notes', {
        header: 'Lồng ghép',
        cell: (info) => {
          const rowIndex = info.row.index
          const isEditing = editingCell?.row === rowIndex && editingCell?.col === 'notes'
          const value = editableData[rowIndex]?.notes || ''

          if (isEditing) {
            return (
              <input
                type="text"
                value={value}
                onChange={(e) => {
                  const newData = [...editableData]
                  newData[rowIndex] = { ...newData[rowIndex], notes: e.target.value }
                  setEditableData(newData)
                }}
                onBlur={() => setEditingCell(null)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') setEditingCell(null)
                }}
                className="w-full px-2 py-1 border rounded"
                autoFocus
              />
            )
          }
          return (
            <div
              onClick={() => setEditingCell({ row: rowIndex, col: 'notes' })}
              className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded"
            >
              {value || <span className="text-gray-400">Click để sửa</span>}
            </div>
          )
        },
      }),
    ],
    [editableData, editingCell, subjects]
  )

  const table = useReactTable({
    data: editableData,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  // Tính toán rowspan cho mỗi ngày
  const getRowSpan = (rowIndex: number) => {
    const currentDay = editableData[rowIndex]?.day_of_week
    if (!currentDay) return 1
    
    let count = 1
    // Đếm số hàng liên tiếp có cùng ngày
    for (let i = rowIndex + 1; i < editableData.length; i++) {
      if (editableData[i]?.day_of_week === currentDay) {
        count++
      } else {
        break
      }
    }
    return count
  }

  // Kiểm tra xem có phải là hàng đầu tiên của ngày không
  const isFirstRowOfDay = (rowIndex: number) => {
    if (rowIndex === 0) return true
    const currentDay = editableData[rowIndex]?.day_of_week
    const prevDay = editableData[rowIndex - 1]?.day_of_week
    return currentDay !== prevDay
  }

  const handleSave = () => {
    const logs = editableData
      .filter((row) => row.subject_name && row.lesson_name)
      .map((row) => ({
        week_number: weekNumber,
        day_of_week: dayMapping[row.day_of_week] || 2,
        period_index: row.period_index,
        subject_name: row.subject_name,
        lesson_name: row.lesson_name,
        notes: row.notes || '',
      }))
    onSave(logs)
  }

  const handleLessonSelect = (lesson: { lesson_index: number; lesson_name: string }, rowIndex: number) => {
    const newData = [...editableData]
    newData[rowIndex] = { ...newData[rowIndex], lesson_name: lesson.lesson_name }
    setEditableData(newData)
    setEditingCell(null)
  }

  return (
    <div className="space-y-4 relative">
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse border border-gray-300">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="bg-gray-100">
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="border border-gray-300 px-4 py-2 text-left font-semibold"
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row, rowIndex) => {
              const isFirstRow = isFirstRowOfDay(rowIndex)
              const rowSpan = isFirstRow ? getRowSpan(rowIndex) : 0
              
              return (
                <tr key={row.id} className="hover:bg-gray-50">
                  {row.getVisibleCells().map((cell, cellIndex) => {
                    // Cột đầu tiên (Thứ) - chỉ hiển thị ở hàng đầu tiên của mỗi ngày
                    if (cellIndex === 0) {
                      if (isFirstRow) {
                        return (
                          <td
                            key={cell.id}
                            rowSpan={rowSpan}
                            className="border border-gray-300 px-4 py-2 align-middle text-center font-medium"
                          >
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </td>
                        )
                      }
                      return null // Không render cell cho các hàng tiếp theo
                    }
                    
                    // Các cột khác - render bình thường
                    return (
                      <td key={cell.id} className="border border-gray-300 px-4 py-2">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          💾 Lưu thay đổi
        </button>
      </div>

      {/* Sidebar danh sách tiết học */}
      {showLessonsSidebar && (
        <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-2xl z-50 border-l border-gray-200 overflow-y-auto">
          <div className="p-4 border-b border-gray-200 sticky top-0 bg-white">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-semibold">Danh sách tiết học</h3>
              <button
                onClick={() => setShowLessonsSidebar(false)}
                className="text-gray-500 hover:text-gray-700 text-xl"
              >
                ×
              </button>
            </div>
            <p className="text-sm text-gray-600">Môn: {selectedSubjectForLessons}</p>
          </div>
          <div className="p-4">
            {lessons.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Chưa có tiết học nào</p>
            ) : (
              <div className="space-y-2">
                {lessons.map((lesson) => (
                  <div
                    key={lesson.lesson_index}
                    onClick={() => {
                      const currentEditing = editingCell
                      if (currentEditing && currentEditing.col === 'lesson_name') {
                        handleLessonSelect(lesson, currentEditing.row)
                        setShowLessonsSidebar(false)
                      }
                    }}
                    className="p-3 border border-gray-200 rounded hover:bg-blue-50 hover:border-blue-300 cursor-pointer transition-colors"
                  >
                    <div className="font-medium text-blue-600">Tiết {lesson.lesson_index}</div>
                    <div className="text-sm text-gray-700 mt-1">{lesson.lesson_name}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

