import { Link, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { ThemeToggle } from './ThemeToggle'

export function Layout() {
  const { token, role, logout } = useAuth()
  const navigate = useNavigate()
  const homePath = role === 'candidate' ? '/apply' : '/'
  const loginPath = role === 'candidate' ? '/apply/login' : '/login'

  return (
    <div className="min-h-screen">
      <header className="border-b border-line dark:border-line-dark">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-4">
          <Link to={homePath} className="flex items-baseline gap-2">
            <span className="text-[15px] font-semibold tracking-tight">Evidentia</span>
            <span className="font-mono text-[11px] text-ink-soft dark:text-ink-soft-dark">recruitment intelligence</span>
          </Link>
          <div className="flex items-center gap-3">
            {token && (
              <button
                onClick={() => {
                  logout()
                  navigate(loginPath)
                }}
                className="text-xs text-ink-soft hover:text-accent dark:text-ink-soft-dark"
              >
                Sign out
              </button>
            )}
            <ThemeToggle />
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-6 py-10">
        <Outlet />
      </main>
    </div>
  )
}
