import { createContext, useContext, useState, type ReactNode } from 'react'

const TOKEN_KEY = 'auth_token'
const ROLE_KEY = 'auth_role'

export type Role = 'recruiter' | 'candidate'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

function setStored(token: string | null, role: Role | null) {
  if (token && role) {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(ROLE_KEY, role)
  } else {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(ROLE_KEY)
  }
}

function getStoredRole(): Role | null {
  const role = localStorage.getItem(ROLE_KEY)
  return role === 'recruiter' || role === 'candidate' ? role : null
}

const AuthContext = createContext<{
  token: string | null
  role: Role | null
  login: (token: string, role: Role) => void
  logout: () => void
} | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(getToken)
  const [role, setRole] = useState<Role | null>(getStoredRole)

  function login(newToken: string, newRole: Role) {
    setStored(newToken, newRole)
    setToken(newToken)
    setRole(newRole)
  }

  function logout() {
    setStored(null, null)
    setToken(null)
    setRole(null)
  }

  return <AuthContext.Provider value={{ token, role, login, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
