import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import type { Job } from '../lib/types'
import { Button, Field, Input, Panel, Textarea } from '../components/ui'

function splitCsv(value: string) {
  return value
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}

export function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState({ title: '', description: '', required: '', preferred: '' })

  useEffect(() => {
    api.listJobs().then(setJobs).finally(() => setLoading(false))
  }, [])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    setCreating(true)
    try {
      const job = await api.createJob({
        title: form.title,
        description: form.description,
        required_skills: splitCsv(form.required),
        preferred_skills: splitCsv(form.preferred),
        rounds: ['technical', 'project', 'behavioral'],
      })
      setJobs((j) => [job, ...j])
      setForm({ title: '', description: '', required: '', preferred: '' })
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="space-y-10">
      <section>
        <h1 className="text-xl font-semibold tracking-tight">Open roles</h1>
        <p className="mt-1 text-sm text-ink-soft dark:text-ink-soft-dark">
          Create a role, then bring candidates through resume matching and an adaptive interview.
        </p>
      </section>

      <section className="grid gap-3 sm:grid-cols-2">
        {loading && <p className="text-sm text-ink-soft dark:text-ink-soft-dark sm:col-span-2">Loading…</p>}
        {!loading && jobs.length === 0 && (
          <p className="text-sm text-ink-soft dark:text-ink-soft-dark sm:col-span-2">No roles yet — create one below.</p>
        )}
        {jobs.map((job) => (
          <Link key={job.id} to={`/jobs/${job.id}`}>
            <Panel className="flex h-full flex-col p-5 transition-colors hover:border-accent">
              <div className="flex items-start justify-between gap-4">
                <h2 className="font-medium">{job.title}</h2>
                <span className="font-mono text-xs text-ink-soft dark:text-ink-soft-dark">#{job.id}</span>
              </div>
              <p className="mt-1 line-clamp-2 text-sm text-ink-soft dark:text-ink-soft-dark">{job.description}</p>
              {job.required_skills.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {job.required_skills.map((s) => (
                    <span key={s} className="rounded-full border border-line px-2 py-0.5 font-mono text-xs text-ink-soft dark:border-line-dark dark:text-ink-soft-dark">
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </Panel>
          </Link>
        ))}
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-soft dark:text-ink-soft-dark">
          New role
        </h2>
        <Panel className="p-5">
          <form onSubmit={handleCreate} className="space-y-4">
            <Field label="Title">
              <Input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Computer Vision Engineer" />
            </Field>
            <Field label="Job description">
              <Textarea required rows={4} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Role responsibilities, context, expectations…" />
            </Field>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Required skills (comma-separated)">
                <Input value={form.required} onChange={(e) => setForm({ ...form, required: e.target.value })} placeholder="Python, OpenCV, Deep Learning" />
              </Field>
              <Field label="Preferred skills (comma-separated)">
                <Input value={form.preferred} onChange={(e) => setForm({ ...form, preferred: e.target.value })} placeholder="YOLO, PyTorch, Docker" />
              </Field>
            </div>
            <Button type="submit" disabled={creating}>
              {creating ? 'Creating…' : 'Create role'}
            </Button>
          </form>
        </Panel>
      </section>
    </div>
  )
}
