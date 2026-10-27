import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import type { Job, MyApplication } from '../lib/types'
import { Badge, Button, Panel } from '../components/ui'

export function CandidatePortalPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [applications, setApplications] = useState<MyApplication[]>([])
  const [applyingJobId, setApplyingJobId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileRefs = useRef<Record<number, HTMLInputElement | null>>({})

  function refreshApplications() {
    api.myApplications().then(setApplications)
  }

  useEffect(() => {
    api.listJobs().then(setJobs)
    refreshApplications()
  }, [])

  async function handleApply(jobId: number) {
    const file = fileRefs.current[jobId]?.files?.[0]
    if (!file) return
    setApplyingJobId(jobId)
    setError(null)
    try {
      await api.apply(jobId, file)
      refreshApplications()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not submit application')
    } finally {
      setApplyingJobId(null)
    }
  }

  const appliedJobIds = new Set(applications.map((a) => a.job_id))

  return (
    <div className="space-y-10">
      <section>
        <h1 className="text-xl font-semibold tracking-tight">Open roles</h1>
        <p className="mt-1 text-sm text-ink-soft dark:text-ink-soft-dark">
          Apply with your resume — we'll match your skills to the role and follow up with an interview.
        </p>
      </section>

      {applications.length > 0 && (
        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-soft dark:text-ink-soft-dark">
            My applications
          </h2>
          <div className="grid gap-3">
            {applications.map((a) => (
              <Panel key={a.id} className="flex items-center justify-between gap-4 p-5">
                <div>
                  <p className="font-medium">{a.job_title}</p>
                  <p className="text-xs text-ink-soft dark:text-ink-soft-dark">Application #{a.id}</p>
                </div>
                <Link to={`/candidates/${a.id}/interview`}>
                  <Button variant="ghost">Continue to interview</Button>
                </Link>
              </Panel>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-soft dark:text-ink-soft-dark">
          Available roles
        </h2>
        <div className="grid gap-3">
          {jobs.length === 0 && <p className="text-sm text-ink-soft dark:text-ink-soft-dark">No open roles right now.</p>}
          {jobs.map((job) => (
            <Panel key={job.id} className="p-5">
              <h3 className="font-medium">{job.title}</h3>
              <p className="mt-1 text-sm text-ink-soft dark:text-ink-soft-dark">{job.description}</p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {job.required_skills.map((s) => (
                  <Badge key={s}>{s}</Badge>
                ))}
              </div>
              <div className="mt-4">
                {appliedJobIds.has(job.id) ? (
                  <Badge tone="good">already applied</Badge>
                ) : (
                  <div className="flex flex-wrap items-center gap-3">
                    <input
                      ref={(el) => {
                        fileRefs.current[job.id] = el
                      }}
                      type="file"
                      accept=".pdf,.docx"
                      className="text-sm text-ink-soft file:mr-3 file:appearance-none file:rounded-md file:border file:border-line file:bg-paper file:px-3 file:py-1.5 file:text-sm file:text-ink hover:file:border-accent dark:text-ink-soft-dark dark:file:border-line-dark dark:file:bg-paper-dark dark:file:text-ink-dark"
                    />
                    <Button onClick={() => handleApply(job.id)} disabled={applyingJobId === job.id}>
                      {applyingJobId === job.id ? 'Submitting…' : 'Apply with resume'}
                    </Button>
                  </div>
                )}
              </div>
            </Panel>
          ))}
        </div>
        {error && <p className="mt-3 text-sm text-bad">{error}</p>}
      </section>
    </div>
  )
}
