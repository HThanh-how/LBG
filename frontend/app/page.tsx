'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'

export default function Home() {
  const router = useRouter()
  const { user, token } = useAuthStore()

  useEffect(() => {
    if (token && user) {
      router.push('/dashboard')
    } else {
      router.push('/login')
    }
  }, [token, user, router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Đang chuyển hướng...</h1>
      </div>
    </div>
  )
}

