'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import { uploadAPI, weeklyReportAPI } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { WeeklyReportTable } from '@/components/WeeklyReportTable'

export default function DashboardPage() {
  const router = useRouter()
  const { user, token, logout } = useAuthStore()
  const [weekNumber, setWeekNumber] = useState(1)
  const [reportData, setReportData] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!token) {
      router.push('/login')
      return
    }
    loadWeeklyReport()
  }, [weekNumber, token])

  const loadWeeklyReport = async () => {
    if (!token) return
    setLoading(true)
    try {
      const data = await weeklyReportAPI.getWeeklyReport(weekNumber)
      setReportData(data)
    } catch (err) {
      console.error('Error loading report:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (type: 'tkb' | 'ctgd', file: File) => {
    try {
      if (type === 'tkb') {
        await uploadAPI.uploadTKB(file)
        alert('Upload TKB thành công!')
      } else {
        await uploadAPI.uploadCTGD(file)
        alert('Upload CTGD thành công!')
      }
      loadWeeklyReport()
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail
      let errorMessage = 'Có lỗi xảy ra khi upload'
      if (Array.isArray(errorDetail)) {
        errorMessage = errorDetail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
      } else if (typeof errorDetail === 'string') {
        errorMessage = errorDetail
      } else if (errorDetail) {
        errorMessage = JSON.stringify(errorDetail)
      }
      alert(errorMessage)
    }
  }

  const handleExportPDF = async () => {
    try {
      await weeklyReportAPI.exportPDF(weekNumber)
    } catch (err) {
      alert('Có lỗi xảy ra khi xuất PDF')
    }
  }

  const handleExportExcel = async () => {
    try {
      await weeklyReportAPI.exportExcel(weekNumber)
    } catch (err) {
      alert('Có lỗi xảy ra khi xuất Excel')
    }
  }

  const handleSave = async (logs: any[]) => {
    try {
      await weeklyReportAPI.saveWeeklyReport(weekNumber, logs)
      alert('Lưu thành công!')
    } catch (err) {
      alert('Có lỗi xảy ra khi lưu')
    }
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold">Hệ thống Quản lý Lịch Báo Giảng</h1>
            <p className="text-sm text-gray-600">
              {user.full_name} - {user.school_name || 'N/A'}
            </p>
          </div>
          <Button onClick={logout} variant="outline">
            Đăng xuất
          </Button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Upload dữ liệu</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Upload Thời khóa biểu (TKB)</label>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleFileUpload('tkb', file)
                }}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Upload Chương trình giảng dạy (CTGD)</label>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleFileUpload('ctgd', file)
                }}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-4">
              <label className="text-sm font-medium">Tuần:</label>
              <input
                type="number"
                min="1"
                max="40"
                value={weekNumber}
                onChange={(e) => setWeekNumber(parseInt(e.target.value) || 1)}
                className="w-20 px-3 py-2 border rounded-md"
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleExportPDF} variant="outline">
                Xuất PDF
              </Button>
              <Button onClick={handleExportExcel} variant="outline">
                Xuất Excel
              </Button>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-8">Đang tải...</div>
          ) : reportData ? (
            <WeeklyReportTable
              data={reportData.data}
              weekNumber={weekNumber}
              onSave={handleSave}
            />
          ) : (
            <div className="text-center py-8 text-gray-500">
              Chưa có dữ liệu. Vui lòng upload TKB và CTGD trước.
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

