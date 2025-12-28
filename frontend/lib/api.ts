import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_V1_PREFIX = '/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorDetail = error.response?.data?.detail
    if (Array.isArray(errorDetail)) {
      error.formattedMessage = errorDetail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
    } else if (typeof errorDetail === 'string') {
      error.formattedMessage = errorDetail
    } else if (errorDetail) {
      error.formattedMessage = JSON.stringify(errorDetail)
    } else {
      error.formattedMessage = error.message || 'Có lỗi xảy ra'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: async (data: { username: string; password: string; full_name: string; school_name?: string }) => {
    const response = await api.post(`${API_V1_PREFIX}/auth/register`, data)
    return response.data
  },
  login: async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    const response = await api.post(`${API_V1_PREFIX}/auth/token`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
  getCurrentUser: async () => {
    const response = await api.get(`${API_V1_PREFIX}/auth/me`)
    return response.data
  },
}

export const classAPI = {
  getClasses: async () => {
    const response = await api.get(`${API_V1_PREFIX}/classes`)
    return response.data
  },
  createClass: async (data: { class_name: string; grade?: string; school_year?: string }) => {
    const response = await api.post(`${API_V1_PREFIX}/classes`, data)
    return response.data
  },
  deleteClass: async (id: number) => {
    const response = await api.delete(`${API_V1_PREFIX}/classes/${id}`)
    return response.data
  },
}

export const templateAPI = {
  downloadTKB: async () => {
    const response = await api.get(`${API_V1_PREFIX}/templates/tkb`, {
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Mau_TKB.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
  },
  getSubjectsFromTKB: async () => {
    const response = await api.get(`${API_V1_PREFIX}/templates/ctgd/subjects`)
    return response.data
  },
  downloadCTGD: async (subject: string) => {
    const response = await api.get(`${API_V1_PREFIX}/templates/ctgd/${subject}`, {
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `Mau_CTGD_${subject}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  },
}

export const uploadAPI = {
  uploadTKB: async (file: File, classId?: number) => {
    const formData = new FormData()
    formData.append('file', file)
    if (classId) {
      formData.append('class_id', classId.toString())
    }
    const response = await api.post(`${API_V1_PREFIX}/upload/tkb`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
  uploadCTGD: async (file: File, classId?: number, subject?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (classId) {
      formData.append('class_id', classId.toString())
    }
    if (subject) {
      formData.append('subject', subject)
    }
    const response = await api.post(`${API_V1_PREFIX}/upload/ctgd`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

export const weeklyReportAPI = {
  getWeeklyReport: async (weekNumber: number, classId?: number) => {
    const params = classId ? { class_id: classId } : {}
    const response = await api.get(`${API_V1_PREFIX}/weekly-report/${weekNumber}`, { params })
    return response.data
  },
  saveWeeklyReport: async (weekNumber: number, logs: any[], classId?: number) => {
    const data = classId ? { logs, class_id: classId } : { logs }
    const response = await api.post(`${API_V1_PREFIX}/weekly-report/${weekNumber}/save`, data)
    return response.data
  },
  getLessonsBySubject: async (subjectName: string) => {
    const response = await api.get(`${API_V1_PREFIX}/weekly-report/lessons/${encodeURIComponent(subjectName)}`)
    return response.data
  },
  exportPDF: async (weekNumber: number, classId?: number) => {
    const params = classId ? { class_id: classId } : {}
    const response = await api.get(`${API_V1_PREFIX}/weekly-report/${weekNumber}/export/pdf`, {
      params,
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `bao_giang_tuan_${weekNumber}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  },
  exportExcel: async (weekNumber: number, classId?: number) => {
    const params = classId ? { class_id: classId } : {}
    const response = await api.get(`${API_V1_PREFIX}/weekly-report/${weekNumber}/export/excel`, {
      params,
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `bao_giang_tuan_${weekNumber}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  },
  previewAllWeeks: async (startWeek: number, endWeek: number, classId?: number) => {
    const params = new URLSearchParams({
      start_week: startWeek.toString(),
      end_week: endWeek.toString(),
    })
    if (classId) {
      params.append('class_id', classId.toString())
    }
    // Mở preview trong tab mới (trả về HTML)
    const previewUrl = `${API_URL}${API_V1_PREFIX}/weekly-report/preview?${params.toString()}`
    window.open(previewUrl, '_blank')
  },
  exportAllWeeks: async (startWeek: number, endWeek: number, classId?: number) => {
    const params = classId ? { class_id: classId } : {}
    const response = await api.get(`${API_V1_PREFIX}/weekly-report/export/all`, {
      params: { ...params, start_week: startWeek, end_week: endWeek },
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `bao_giang_tuan_${startWeek}_${endWeek}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  },
}

export const holidayAPI = {
  getHolidays: async () => {
    const response = await api.get(`${API_V1_PREFIX}/holidays`)
    return response.data
  },
  createHoliday: async (data: {
    holiday_date?: string
    holiday_name: string
    week_number?: number
    start_date?: string
    end_date?: string
    is_odd_day?: number
    is_even_day?: number
  }) => {
    const response = await api.post(`${API_V1_PREFIX}/holidays`, data)
    return response.data
  },
  deleteHoliday: async (id: number) => {
    const response = await api.delete(`${API_V1_PREFIX}/holidays/${id}`)
    return response.data
  },
}
