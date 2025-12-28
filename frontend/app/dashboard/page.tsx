'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import { uploadAPI, weeklyReportAPI, templateAPI } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { WeeklyReportTable } from '@/components/WeeklyReportTable'

export default function DashboardPage() {
  const router = useRouter()
  const { user, token, logout } = useAuthStore()
  const [reportData, setReportData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [selectedWeeks, setSelectedWeeks] = useState<number[]>([1])
  const [weekDataMap, setWeekDataMap] = useState<{ [key: number]: any }>({})
  const [activeTab, setActiveTab] = useState(1)
  const [contextMenu, setContextMenu] = useState<{ week: number; x: number; y: number } | null>(null)
  const [showWeekConfig, setShowWeekConfig] = useState(false)
  const [startDate, setStartDate] = useState<string>(() => {
    const date = new Date()
    date.setMonth(8) // Tháng 9
    date.setDate(1)
    return date.toISOString().split('T')[0]
  })
  const [endWeek, setEndWeek] = useState(54)
  const [holidayWeeks, setHolidayWeeks] = useState<number[]>([])
  const [holidayConfigs, setHolidayConfigs] = useState<Array<{
    weekNumber?: number
    startDate?: string
    endDate?: string
    isOddDay?: boolean
    isEvenDay?: boolean
    holidayName: string
  }>>([])
  const [subjects, setSubjects] = useState<string[]>([])
  const [selectedSubject, setSelectedSubject] = useState<string>('')

  useEffect(() => {
    if (!token) {
      router.push('/login')
      return
    }
    // Chỉ load tuần đang active và các tuần xung quanh để tối ưu
    loadActiveWeek()
  }, [activeTab, token])

  useEffect(() => {
    if (!token) return
    // Load tuần đầu tiên khi mount
    if (activeTab && !weekDataMap[activeTab]) {
      loadWeeklyReport(activeTab)
    }
    // Load danh sách môn học từ TKB
    loadSubjects()
  }, [])

  const loadSubjects = async () => {
    try {
      const subjectsList = await templateAPI.getSubjectsFromTKB()
      setSubjects(subjectsList)
      if (subjectsList.length > 0) {
        setSelectedSubject(subjectsList[0])
      }
    } catch (err) {
      console.error('Error loading subjects:', err)
    }
  }

  const loadActiveWeek = async () => {
    if (!token || !activeTab) return
    if (weekDataMap[activeTab]) {
      setReportData(weekDataMap[activeTab])
      return
    }
    setLoading(true)
    try {
      const data = await weeklyReportAPI.getWeeklyReport(activeTab)
      setWeekDataMap(prev => ({ ...prev, [activeTab]: data }))
      setReportData(data)
    } catch (err) {
      console.error('Error loading report:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadWeeklyReport = async (week: number) => {
    if (!token) return
    try {
      const data = await weeklyReportAPI.getWeeklyReport(week)
      setWeekDataMap(prev => ({ ...prev, [week]: data }))
      if (week === activeTab) {
        setReportData(data)
      }
    } catch (err) {
      console.error('Error loading report:', err)
    }
  }

  const getWeekDates = (weekNumber: number) => {
    if (!startDate) return { start: new Date(), end: new Date() }
    
    // Tính từ ngày bắt đầu đã chọn
    const start = new Date(startDate)
    let firstMonday = new Date(start)
    
    // Tìm thứ 2 đầu tiên
    while (firstMonday.getDay() !== 1) {
      firstMonday.setDate(firstMonday.getDate() + 1)
    }
    
    // Tính tuần bắt đầu (thứ 2) và kết thúc (thứ 6)
    const weekStart = new Date(firstMonday)
    weekStart.setDate(firstMonday.getDate() + (weekNumber - 1) * 7)
    
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekStart.getDate() + 4) // Thứ 2 đến thứ 6 (5 ngày)
    
    return { start: weekStart, end: weekEnd }
  }

  const formatDate = (date: Date) => {
    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const year = date.getFullYear()
    return `${day}/${month}/${year}`
  }

  const handleRemoveWeek = (week: number) => {
    if (selectedWeeks.length > 1) {
      if (window.confirm(`Bạn có chắc muốn xóa Tuần ${week}?`)) {
        const newWeeks = selectedWeeks.filter(w => w !== week)
        setSelectedWeeks(newWeeks)
        if (activeTab === week) {
          const nextWeek = newWeeks[0] || 1
          setActiveTab(nextWeek)
          if (weekDataMap[nextWeek]) {
            setReportData(weekDataMap[nextWeek])
          } else {
            loadWeeklyReport(nextWeek)
          }
        }
        // Xóa data của tuần đã xóa
        setWeekDataMap(prev => {
          const newMap = { ...prev }
          delete newMap[week]
          return newMap
        })
      }
    }
  }

  const handleDuplicateWeek = (week: number) => {
    const maxWeek = Math.max(...selectedWeeks, 0)
    const newWeek = maxWeek + 1
    if (newWeek <= 54) {
      // Copy data từ tuần gốc
      if (weekDataMap[week]) {
        const duplicatedData = JSON.parse(JSON.stringify(weekDataMap[week]))
        setWeekDataMap(prev => ({ ...prev, [newWeek]: duplicatedData }))
      }
      setSelectedWeeks([...selectedWeeks, newWeek].sort((a, b) => a - b))
      setActiveTab(newWeek)
      // Load data nếu chưa có
      if (!weekDataMap[week]) {
        loadWeeklyReport(week).then(() => {
          if (weekDataMap[week]) {
            const duplicatedData = JSON.parse(JSON.stringify(weekDataMap[week]))
            setWeekDataMap(prev => ({ ...prev, [newWeek]: duplicatedData }))
          }
        })
      }
    } else {
      alert('Đã đạt giới hạn 54 tuần')
    }
  }

  const handleApplyWeekConfig = async () => {
    if (!startDate) {
      alert('Vui lòng chọn ngày bắt đầu')
      return
    }
    
    // Lưu cấu hình nghỉ lễ vào backend
    try {
      const { holidayAPI } = await import('@/lib/api')
      
      // Tạo các nghỉ lễ mới
      for (const config of holidayConfigs) {
        if (config.holidayName) {
          if (config.startDate && config.endDate) {
            // Nghỉ theo khoảng ngày
              await holidayAPI.createHoliday({
                holiday_name: config.holidayName,
                start_date: config.startDate,
                end_date: config.endDate,
                is_odd_day: config.isOddDay ? 1 : undefined,
                is_even_day: config.isEvenDay ? 1 : undefined,
              })
          } else if (config.weekNumber) {
            // Nghỉ theo tuần
            await holidayAPI.createHoliday({
              holiday_name: config.holidayName,
              week_number: config.weekNumber,
              is_odd_day: config.isOddDay ? 1 : undefined,
              is_even_day: config.isEvenDay ? 1 : undefined,
            })
          }
        }
      }
    } catch (err) {
      console.error('Error saving holiday config:', err)
      alert('Có lỗi khi lưu cấu hình nghỉ lễ: ' + (err as any).message)
    }
    
    // Tính toán tuần dựa trên nghỉ lễ
    const weeks: number[] = []
    for (let i = 1; i <= endWeek; i++) {
      const shouldExclude = holidayConfigs.some(config => 
        config.weekNumber === i
      )
      if (!shouldExclude) {
        weeks.push(i)
      }
    }
    
    setSelectedWeeks(weeks)
    if (weeks.length > 0) {
      setActiveTab(weeks[0])
      if (!weekDataMap[weeks[0]]) {
        loadWeeklyReport(weeks[0])
      }
    }
    setShowWeekConfig(false)
  }

  const handleContextMenu = (e: React.MouseEvent, week: number) => {
    e.preventDefault()
    setContextMenu({ week, x: e.clientX, y: e.clientY })
  }

  const handleCloseContextMenu = () => {
    setContextMenu(null)
  }

  useEffect(() => {
    const handleClick = () => {
      setContextMenu(null)
    }
    if (contextMenu) {
      document.addEventListener('click', handleClick)
      return () => document.removeEventListener('click', handleClick)
    }
  }, [contextMenu])

  const handleTabChange = (week: number) => {
    setActiveTab(week)
    if (weekDataMap[week]) {
      setReportData(weekDataMap[week])
    } else {
      setLoading(true)
      loadWeeklyReport(week)
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
      loadActiveWeek()
      loadSubjects()
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

  const handleExportPDF = async (week: number = activeTab) => {
    try {
      await weeklyReportAPI.exportPDF(week)
    } catch (err) {
      alert('Có lỗi xảy ra khi xuất PDF')
    }
  }

  const handleExportExcel = async (week: number = activeTab) => {
    try {
      await weeklyReportAPI.exportExcel(week)
    } catch (err) {
      alert('Có lỗi xảy ra khi xuất Excel')
    }
  }

  const handleSave = async (logs: any[]) => {
    try {
      await weeklyReportAPI.saveWeeklyReport(activeTab, logs)
      alert('Lưu thành công!')
      // Reload data sau khi lưu
      loadWeeklyReport(activeTab)
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
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <label className="block text-sm font-medium">Upload Thời khóa biểu (TKB)</label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    try {
                      await templateAPI.downloadTKB()
                    } catch (err: any) {
                      console.error('Error downloading TKB template:', err)
                      alert('Có lỗi xảy ra khi tải mẫu TKB: ' + (err.message || 'Unknown error'))
                    }
                  }}
                  className="text-xs"
                >
                  Tải mẫu
                </Button>
              </div>
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
              <div className="flex items-center gap-2 mb-2">
                <label className="block text-sm font-medium">Upload Chương trình giảng dạy (CTGD)</label>
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="px-2 py-1 text-xs border border-gray-300 rounded bg-white text-gray-900"
                  disabled={subjects.length === 0}
                >
                  {subjects.length === 0 ? (
                    <option value="">Chưa có môn (upload TKB trước)</option>
                  ) : (
                    subjects.map((subject) => (
                      <option key={subject} value={subject}>
                        {subject}
                      </option>
                    ))
                  )}
                </select>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    if (selectedSubject) {
                      try {
                        await templateAPI.downloadCTGD(selectedSubject)
                      } catch (err: any) {
                        console.error('Error downloading CTGD template:', err)
                        alert('Có lỗi xảy ra khi tải mẫu CTGD: ' + (err.message || 'Unknown error'))
                      }
                    } else {
                      alert('Vui lòng chọn môn học hoặc upload TKB trước')
                    }
                  }}
                  className="text-xs"
                  disabled={!selectedSubject}
                >
                  Tải mẫu
                </Button>
              </div>
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
          <p className="text-xs text-gray-500">
            💡 Tải file mẫu để xem định dạng, sau đó điền dữ liệu và upload lại
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-600">
                Tổng số tuần: {selectedWeeks.length}
              </div>
              <Button
                onClick={() => setShowWeekConfig(true)}
                variant="outline"
                size="sm"
                className="text-xs"
              >
                ⚙️ Cấu hình tuần
              </Button>
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={() => handleExportPDF(activeTab)} 
                variant="outline"
                size="sm"
              >
                Xuất PDF
              </Button>
              <Button 
                onClick={() => handleExportExcel(activeTab)} 
                variant="outline"
                size="sm"
              >
                Xuất Excel
              </Button>
              <Button 
                onClick={async () => {
                  const startWeek = Math.min(...selectedWeeks)
                  const endWeek = Math.max(...selectedWeeks)
                  try {
                    await weeklyReportAPI.exportAllWeeks(startWeek, endWeek)
                  } catch (err) {
                    alert('Có lỗi xảy ra khi preview')
                  }
                }} 
                variant="outline"
                size="sm"
              >
                Preview
              </Button>
            </div>
          </div>

          {/* Tabs cho các tuần */}
          <div className="border-b border-gray-200 mb-4 relative">
            <div className="flex gap-2 overflow-x-auto">
              {selectedWeeks.map((week) => {
                const { start, end } = getWeekDates(week)
                return (
                  <button
                    key={week}
                    onClick={() => handleTabChange(week)}
                    onContextMenu={(e) => handleContextMenu(e, week)}
                    className={`
                      px-3 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap text-left
                      ${activeTab === week
                        ? 'border-blue-500 text-blue-600 bg-blue-50'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }
                    `}
                    title={`${formatDate(start)} - ${formatDate(end)}`}
                  >
                    <div className="font-semibold">Tuần {week}</div>
                    <div className="text-xs font-normal opacity-75 mt-0.5">
                      {formatDate(start)} - {formatDate(end)}
                    </div>
                  </button>
                )
              })}
            </div>

            {/* Context Menu */}
            {contextMenu && (
              <div
                className="fixed bg-white border border-gray-200 rounded-md shadow-lg z-50 py-1 min-w-[150px]"
                style={{
                  left: `${contextMenu.x}px`,
                  top: `${contextMenu.y}px`,
                }}
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  onClick={() => {
                    handleDuplicateWeek(contextMenu.week)
                    handleCloseContextMenu()
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Nhân đôi tuần {contextMenu.week}
                </button>
                {selectedWeeks.length > 1 && (
                  <button
                    onClick={() => {
                      handleRemoveWeek(contextMenu.week)
                      handleCloseContextMenu()
                    }}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    Xóa tuần {contextMenu.week}
                  </button>
                )}
              </div>
            )}
          </div>

          {loading ? (
            <div className="text-center py-8">Đang tải...</div>
          ) : reportData ? (
            <WeeklyReportTable
              data={reportData.data}
              weekNumber={activeTab}
              onSave={handleSave}
            />
          ) : (
            <div className="text-center py-8 text-gray-500">
              Chưa có dữ liệu. Vui lòng upload TKB và CTGD trước.
            </div>
          )}
        </div>

        {/* Modal cấu hình tuần */}
        {showWeekConfig && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
              <h3 className="text-lg font-semibold mb-4">Cấu hình tuần học</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Ngày bắt đầu năm học:
                  </label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Ngày này sẽ là cơ sở để tính các tuần học
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Tuần kết thúc (1-54):
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="54"
                    value={endWeek}
                    onChange={(e) => setEndWeek(parseInt(e.target.value) || 54)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Cấu hình nghỉ lễ:
                  </label>
                  <div className="space-y-3 max-h-60 overflow-y-auto border border-gray-200 rounded p-3">
                    {holidayConfigs.map((config, index) => (
                      <div key={index} className="bg-gray-50 p-3 rounded border">
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-sm font-medium">Nghỉ lễ {index + 1}</span>
                          <button
                            type="button"
                            onClick={() => {
                              setHolidayConfigs(holidayConfigs.filter((_, i) => i !== index))
                            }}
                            className="text-red-500 text-xs hover:text-red-700"
                          >
                            × Xóa
                          </button>
                        </div>
                        <div className="space-y-2">
                          <input
                            type="text"
                            placeholder="Tên nghỉ lễ (ví dụ: Tết Nguyên Đán)"
                            value={config.holidayName}
                            onChange={(e) => {
                              const newConfigs = [...holidayConfigs]
                              newConfigs[index].holidayName = e.target.value
                              setHolidayConfigs(newConfigs)
                            }}
                            className="w-full px-2 py-1 text-xs border border-gray-300 rounded bg-white text-gray-900"
                          />
                          <div className="grid grid-cols-2 gap-2">
                            <div>
                              <label className="text-xs text-gray-600">Tuần (tùy chọn):</label>
                              <input
                                type="number"
                                min="1"
                                max="54"
                                placeholder="VD: 5"
                                value={config.weekNumber || ''}
                                onChange={(e) => {
                                  const newConfigs = [...holidayConfigs]
                                  newConfigs[index].weekNumber = e.target.value ? parseInt(e.target.value) : undefined
                                  setHolidayConfigs(newConfigs)
                                }}
                                className="w-full px-2 py-1 text-xs border border-gray-300 rounded bg-white text-gray-900"
                              />
                            </div>
                            <div>
                              <label className="text-xs text-gray-600">Từ ngày:</label>
                              <input
                                type="date"
                                value={config.startDate || ''}
                                onChange={(e) => {
                                  const newConfigs = [...holidayConfigs]
                                  newConfigs[index].startDate = e.target.value
                                  setHolidayConfigs(newConfigs)
                                }}
                                className="w-full px-2 py-1 text-xs border border-gray-300 rounded bg-white text-gray-900"
                              />
                            </div>
                            <div>
                              <label className="text-xs text-gray-600">Đến ngày:</label>
                              <input
                                type="date"
                                value={config.endDate || ''}
                                onChange={(e) => {
                                  const newConfigs = [...holidayConfigs]
                                  newConfigs[index].endDate = e.target.value
                                  setHolidayConfigs(newConfigs)
                                }}
                                className="w-full px-2 py-1 text-xs border border-gray-300 rounded bg-white text-gray-900"
                              />
                            </div>
                            <div>
                              <label className="text-xs text-gray-600">Loại ngày:</label>
                              <select
                                value={config.isOddDay ? 'odd' : config.isEvenDay ? 'even' : 'all'}
                                onChange={(e) => {
                                  const newConfigs = [...holidayConfigs]
                                  newConfigs[index].isOddDay = e.target.value === 'odd'
                                  newConfigs[index].isEvenDay = e.target.value === 'even'
                                  setHolidayConfigs(newConfigs)
                                }}
                                className="w-full px-2 py-1 text-xs border border-gray-300 rounded bg-white text-gray-900"
                              >
                                <option value="all">Tất cả</option>
                                <option value="odd">Ngày lẻ</option>
                                <option value="even">Ngày chẵn</option>
                              </select>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                    <button
                      type="button"
                      onClick={() => {
                        setHolidayConfigs([...holidayConfigs, {
                          holidayName: '',
                          weekNumber: undefined,
                          startDate: undefined,
                          endDate: undefined,
                          isOddDay: false,
                          isEvenDay: false,
                        }])
                      }}
                      className="w-full px-3 py-2 text-xs border border-gray-300 rounded bg-white text-gray-700 hover:bg-gray-50"
                    >
                      + Thêm nghỉ lễ
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Có thể cấu hình nghỉ theo tuần, theo khoảng ngày, hoặc theo ngày lẻ/chẵn
                  </p>
                </div>

                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-sm font-medium mb-2">Xem trước:</p>
                  <p className="text-xs text-gray-600">
                    Sẽ tạo từ Tuần 1 đến Tuần {endWeek}
                    {startDate && (
                      <span className="block mt-1">
                        Bắt đầu từ: {new Date(startDate).toLocaleDateString('vi-VN')}
                      </span>
                    )}
                    {holidayWeeks.length > 0 && (
                      <span className="block mt-1">
                        Loại trừ: Tuần {holidayWeeks.join(', ')}
                      </span>
                    )}
                    <span className="block mt-1 font-semibold">
                      Tổng: {Math.max(0, endWeek - holidayWeeks.filter(w => w >= 1 && w <= endWeek).length)} tuần
                    </span>
                  </p>
                </div>
              </div>

              <div className="flex gap-2 mt-6">
                <Button
                  onClick={handleApplyWeekConfig}
                  variant="default"
                  className="flex-1"
                >
                  Áp dụng
                </Button>
                <Button
                  onClick={() => setShowWeekConfig(false)}
                  variant="outline"
                  className="flex-1"
                >
                  Hủy
                </Button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

