'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import { authAPI } from '@/lib/api'

export default function Home() {
  const router = useRouter()
  const { user, setUser, setToken } = useAuthStore()

  useEffect(() => {
    // TẠM THỜI TẮT AUTHENTICATION - Tự động lấy user và vào dashboard
    const autoLogin = async () => {
      try {
        // Gọi API để lấy user (backend sẽ tự động trả về user đầu tiên)
        const userData = await authAPI.getCurrentUser()
        setUser(userData)
        // Set một token giả để frontend không redirect về login
        setToken('bypass_token')
        router.push('/dashboard')
      } catch (error) {
        // Nếu có lỗi, vẫn vào dashboard (backend đã bypass auth)
        router.push('/dashboard')
      }
    }
    
    if (!user) {
      autoLogin()
    } else {
      router.push('/dashboard')
    }
  }, [user, router, setUser, setToken])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Đang chuyển hướng...</h1>
      </div>
    </div>
  )
}


