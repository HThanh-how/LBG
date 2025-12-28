'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import { authAPI } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function LoginPage() {
  const router = useRouter()
  const { setUser, setToken } = useAuthStore()
  
  // TẠM THỜI TẮT AUTHENTICATION - Tự động redirect đến dashboard
  useEffect(() => {
    const autoLogin = async () => {
      try {
        const userData = await authAPI.getCurrentUser()
        setUser(userData)
        setToken('bypass_token')
        router.push('/dashboard')
      } catch (error) {
        // Vẫn vào dashboard nếu có lỗi
        router.push('/dashboard')
      }
    }
    autoLogin()
  }, [router, setUser, setToken])
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    full_name: '',
    school_name: '',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      if (isLogin) {
        const response = await authAPI.login(formData.username, formData.password)
        setToken(response.access_token)
        const user = await authAPI.getCurrentUser()
        setUser(user)
        router.push('/dashboard')
      } else {
        await authAPI.register({
          username: formData.username,
          password: formData.password,
          full_name: formData.full_name,
          school_name: formData.school_name,
        })
        setSuccess('Đăng ký thành công! Vui lòng đăng nhập.')
        setError('')
        setIsLogin(true)
        setFormData({ username: '', password: '', full_name: '', school_name: '' })
      }
    } catch (err: any) {
      const errorMessage = err.formattedMessage || err.response?.data?.detail || err.message || 'Có lỗi xảy ra'
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage))
      setSuccess('')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center mb-6">
          {isLogin ? 'Đăng nhập' : 'Đăng ký'}
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <>
              <div>
                <label className="block text-sm font-medium mb-1">Họ và tên</label>
                <Input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  required={!isLogin}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Tên trường</label>
                <Input
                  type="text"
                  value={formData.school_name}
                  onChange={(e) => setFormData({ ...formData, school_name: e.target.value })}
                />
              </div>
            </>
          )}
          <div>
            <label className="block text-sm font-medium mb-1">Tên đăng nhập</label>
            <Input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Mật khẩu</label>
            <Input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />
          </div>
          {success && (
            <div className="p-3 text-sm text-green-600 bg-green-50 rounded border border-green-200">
              {success}
            </div>
          )}
          {error && (
            <div className="p-3 text-sm text-red-600 bg-red-50 rounded border border-red-200">
              {error}
            </div>
          )}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Đang xử lý...' : isLogin ? 'Đăng nhập' : 'Đăng ký'}
          </Button>
        </form>
        <div className="mt-4 text-center">
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin)
              setError('')
              setSuccess('')
            }}
            className="text-sm text-blue-600 hover:underline"
          >
            {isLogin ? 'Chưa có tài khoản? Đăng ký' : 'Đã có tài khoản? Đăng nhập'}
          </button>
        </div>
      </div>
    </div>
  )
}

