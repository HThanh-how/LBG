import { create } from 'zustand'

interface User {
  id: number
  username: string
  full_name: string
  school_name?: string
}

interface AuthState {
  user: User | null
  token: string | null
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  setUser: (user) => set({ user }),
  setToken: (token) => {
    set({ token })
    if (token) {
      localStorage.setItem('access_token', token)
    } else {
      localStorage.removeItem('access_token')
    }
  },
  logout: () => {
    set({ user: null, token: null })
    localStorage.removeItem('access_token')
  },
}))

