import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../lib/api'
import type { Report } from '../lib/types'
import { ReportView } from '../components/ReportView'

export function ReportPage() {
  const { interviewId } = useParams()
  const [report, setReport] = useState<Report | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!interviewId) return
    api.getReport(Number(interviewId)).then(setReport).catch((e) => setError(e.message))
  }, [interviewId])

  return (
    <div className="space-y-6">
      <Link to="/" className="text-xs text-ink-soft hover:text-accent dark:text-ink-soft-dark">
        ← All roles
      </Link>
      {error && <p className="text-sm text-bad">Could not load report: {error}</p>}
      {!report && !error && <p className="text-sm text-ink-soft dark:text-ink-soft-dark">Loading…</p>}
      {report && <ReportView report={report} />}
    </div>
  )
}
