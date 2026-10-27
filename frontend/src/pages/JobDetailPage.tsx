import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../lib/api'
import type { Candidate, InterviewSummary, Job } from '../lib/types'
import { Badge, Button, Panel } from '../components/ui'

function scoreTone(score: number | null): 'neutral' | 'good' | 'warn' | 'bad' {
  if (score === null) return 'neutral'
  if (score >= 0.7) return 'good'
  if (score >= 0.4) return 'warn'
  return 'bad'
}

export function JobDetailPage() {
  const { jobId } = useParams()
  const [job, setJob] = useState<Job | null>(null)
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [interviews, setInterviews] = useState<Record<number, InterviewSummary[]>>({})
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!jobId) return
    api.getJob(Number(jobId)).then(setJob)
    api.listCandidates(Number(jobId)).then((cs) => {
      setCandidates(cs)
      cs.forEach((c) => {
        api.listCandidateInterviews(c.id).then((ivs) => setInterviews((prev) => ({ ...prev, [c.id]: ivs })))
      })
    })
  }, [jobId])

  function completedInterview(candidateId: number): InterviewSummary | undefined {
    return interviews[candidateId]?.find((i) => i.status === 'complete')
  }

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault()
    const file = fileRef.current?.files?.[0]
    if (!file || !jobId) return
    setUploading(true)
    setError(null)
    try {
      const candidate = await api.uploadResume(Number(jobId), file)
      setCandidates((c) => [candidate, ...c])
      if (fileRef.current) fileRef.current.value = ''
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  if (!job) return <p className="text-sm text-ink-soft dark:text-ink-soft-dark">Loading…</p>

  return (
    <div className="space-y-10">
      <section>
        <Link to="/" className="text-xs text-ink-soft hover:text-accent dark:text-ink-soft-dark">
          ← All roles
        </Link>
        <h1 className="mt-2 text-xl font-semibold tracking-tight">{job.title}</h1>
        <p className="mt-2 max-w-2xl text-sm text-ink-soft dark:text-ink-soft-dark">{job.description}</p>
        <div className="mt-4 flex flex-wrap gap-1.5">
          {job.required_skills.map((s) => (
            <Badge key={s}>{s}</Badge>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-soft dark:text-ink-soft-dark">
          Upload resume
        </h2>
        <Panel className="p-5">
          <form onSubmit={handleUpload} className="flex flex-wrap items-center gap-3">
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.docx"
              required
              className="text-sm text-ink-soft file:mr-3 file:appearance-none file:rounded-md file:border file:border-line file:bg-paper file:px-3 file:py-1.5 file:text-sm file:text-ink hover:file:border-accent dark:text-ink-soft-dark dark:file:border-line-dark dark:file:bg-paper-dark dark:file:text-ink-dark"
            />
            <Button type="submit" disabled={uploading}>
              {uploading ? 'Parsing…' : 'Upload & match'}
            </Button>
          </form>
          {error && <p className="mt-3 text-sm text-bad">{error}</p>}
        </Panel>
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-soft dark:text-ink-soft-dark">
          Candidates
        </h2>
        <div className="grid gap-3">
          {candidates.length === 0 && (
            <p className="text-sm text-ink-soft dark:text-ink-soft-dark">No candidates yet.</p>
          )}
          {candidates.map((c) => (
            <Panel key={c.id} className="flex items-center justify-between gap-4 p-5">
              <div>
                <p className="font-medium">{c.name ?? `Candidate #${c.id}`}</p>
                <div className="mt-1.5 flex flex-wrap gap-1.5">
                  {c.resume_profile?.skills.slice(0, 5).map((s) => (
                    <span key={s.name} className="font-mono text-xs text-ink-soft dark:text-ink-soft-dark">
                      {s.name}
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Badge tone={scoreTone(c.match_score)}>
                  {c.match_score !== null ? `${Math.round(c.match_score * 100)}% match` : 'no match score'}
                </Badge>
                {completedInterview(c.id) ? (
                  <Link to={`/interviews/${completedInterview(c.id)!.id}/report`}>
                    <Button variant="ghost">View report</Button>
                  </Link>
                ) : (
                  <Link to={`/candidates/${c.id}/interview`}>
                    <Button variant="ghost">Interview</Button>
                  </Link>
                )}
              </div>
            </Panel>
          ))}
        </div>
      </section>
    </div>
  )
}
