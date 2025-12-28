'use client'

import { useState, useMemo, useEffect } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
} from '@tanstack/react-table'

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
}

const columnHelper = createColumnHelper<ReportRow>()

export function WeeklyReportTable({ data, weekNumber, onSave }: WeeklyReportTableProps) {
  const [editableData, setEditableData] = useState<ReportRow[]>(data)
  const [editingCell, setEditingCell] = useState<{ row: number; col: string } | null>(null)

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
              <input
                type="text"
                value={value}
                onChange={(e) => {
                  const newData = [...editableData]
                  newData[rowIndex] = { ...newData[rowIndex], subject_name: e.target.value }
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
              onClick={() => setEditingCell({ row: rowIndex, col: 'subject_name' })}
              className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded"
            >
              {value || <span className="text-gray-400">Click để sửa</span>}
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
              onClick={() => setEditingCell({ row: rowIndex, col: 'lesson_name' })}
              className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded"
            >
              {value || <span className="text-gray-400">Click để sửa</span>}
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
    [editableData, editingCell]
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

  return (
    <div className="space-y-4">
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
          Lưu thay đổi
        </button>
      </div>
    </div>
  )
}

