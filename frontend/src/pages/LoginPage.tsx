import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuth, type Role } from '../lib/auth'
import { Button, Field, Input, Panel } from '../components/ui'

export function LoginPage({ role, redirectTo }: { role: Role; redirectTo: string }) {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const roleLabel = role === 'recruiter' ? 'Recruiter' : 'Candidate'

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      if (mode === 'register') {
        await api.register(email, password, role)
      }
      const { access_token, role: loggedInRole } = await api.login(email, password)
      if (loggedInRole !== role) {
        throw new Error(`That account is a ${loggedInRole} account — use the ${loggedInRole} sign-in page instead.`)
      }
      login(access_token, loggedInRole)
      navigate(redirectTo)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-sm">
      <h1 className="text-xl font-semibold tracking-tight">
        {mode === 'login' ? `${roleLabel} sign in` : `Create a ${roleLabel.toLowerCase()} account`}
      </h1>
      <Panel className="mt-5 p-5">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Email">
            <Input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </Field>
          <Field label="Password">
            <Input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} />
          </Field>
          {error && <p className="text-sm text-bad">{error}</p>}
          <Button type="submit" disabled={busy} className="w-full">
            {busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
          </Button>
        </form>
      </Panel>
      <button
        onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
        className="mt-4 block text-xs text-ink-soft hover:text-accent dark:text-ink-soft-dark"
      >
        {mode === 'login' ? "Don't have an account? Create one" : 'Already have an account? Sign in'}
      </button>
      <Link
        to={role === 'recruiter' ? '/apply/login' : '/login'}
        className="mt-2 block text-xs text-ink-soft hover:text-accent dark:text-ink-soft-dark"
      >
        {role === 'recruiter' ? 'Applying for a job? Candidate sign in →' : 'Hiring? Recruiter sign in →'}
      </Link>
    </div>
  )
}
