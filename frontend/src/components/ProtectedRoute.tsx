import { Navigate, Outlet } from 'react-router-dom'
import { useAuth, type Role } from '../lib/auth'

export function ProtectedRoute({ role }: { role: Role }) {
  const { token, role: currentRole } = useAuth()
  const loginPath = role === 'recruiter' ? '/login' : '/apply/login'
  if (!token || currentRole !== role) return <Navigate to={loginPath} replace />
  return <Outlet />
}
