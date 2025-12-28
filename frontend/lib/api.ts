import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_V1_PREFIX = '/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
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

export const uploadAPI = {
  uploadTKB: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post(`${API_V1_PREFIX}/upload/tkb`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
  uploadCTGD: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post(`${API_V1_PREFIX}/upload/ctgd`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

export const weeklyReportAPI = {
  getWeeklyReport: async (weekNumber: number) => {
    const response = await api.get(`${API_V1_PREFIX}/weekly-report/${weekNumber}`)
    return response.data
  },
  saveWeeklyReport: async (weekNumber: number, logs: any[]) => {
    const response = await api.post(`${API_V1_PREFIX}/weekly-report/${weekNumber}/save`, logs)
    return response.data
  },
  exportPDF: async (weekNumber: number) => {
    const response = await api.get(`${API_V1_PREFIX}/weekly-report/${weekNumber}/export/pdf`, {
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
  exportExcel: async (weekNumber: number) => {
    const response = await api.get(`${API_V1_PREFIX}/weekly-report/${weekNumber}/export/excel`, {
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
}

