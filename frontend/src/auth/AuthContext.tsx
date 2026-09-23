import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { getCurrentUser, login as loginRequest } from '../api/auth'
import { clearAuthToken, getAuthToken, setAuthToken } from '../api/client'
import type { User } from '../types/user'

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<User>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!getAuthToken()) {
      setLoading(false)
      return
    }
    getCurrentUser()
      .then(setUser)
      .catch(() => clearAuthToken())
      .finally(() => setLoading(false))
  }, [])

  async function login(email: string, password: string): Promise<User> {
    const result = await loginRequest(email, password)
    setAuthToken(result.access_token)
    setUser(result.user)
    return result.user
  }

  function logout() {
    clearAuthToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
