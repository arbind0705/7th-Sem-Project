import type {
  AudioRespondResult,
  Candidate,
  InterviewSummary,
  Job,
  MyApplication,
  Report,
  RespondResult,
  StartInterviewResponse,
} from './types'
import type { Role } from './auth'
import { getToken } from './auth'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function authHeaders(): Record<string, string> {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...authHeaders(), ...init?.headers },
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${body}`)
  }
  return res.json()
}

export const api = {
  register: (email: string, password: string, role: Role) =>
    request<{ id: number; email: string; role: Role }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, role }),
    }),
  login: (email: string, password: string) =>
    request<{ access_token: string; token_type: string; role: Role }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  listJobs: () => request<Job[]>('/api/jobs'),
  createJob: (job: Omit<Job, 'id'>) =>
    request<Job>('/api/jobs', { method: 'POST', body: JSON.stringify(job) }),
  getJob: (id: number) => request<Job>(`/api/jobs/${id}`),
  listCandidates: (jobId: number) => request<Candidate[]>(`/api/jobs/${jobId}/candidates`),
  getCandidate: (id: number) => request<Candidate>(`/api/candidates/${id}`),
  listCandidateInterviews: (candidateId: number) =>
    request<InterviewSummary[]>(`/api/candidates/${candidateId}/interviews`),
  getReport: (interviewId: number) => request<Report>(`/api/interviews/${interviewId}/report`),
  uploadResume: async (jobId: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${BASE_URL}/api/candidates/resumes/upload?job_id=${jobId}`, {
      method: 'POST',
      headers: authHeaders(),
      body: form,
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json() as Promise<Candidate>
  },
  apply: async (jobId: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${BASE_URL}/api/candidates/apply?job_id=${jobId}`, {
      method: 'POST',
      headers: authHeaders(),
      body: form,
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json() as Promise<Candidate>
  },
  myApplications: () => request<MyApplication[]>('/api/candidates/me'),
  startInterview: (candidateId: number) =>
    request<StartInterviewResponse>(`/api/interviews/start?candidate_id=${candidateId}`, {
      method: 'POST',
    }),
  respond: (interviewId: number, answer: string) =>
    request<RespondResult>(`/api/interviews/${interviewId}/respond`, {
      method: 'POST',
      body: JSON.stringify({ answer }),
    }),
  respondAudio: async (interviewId: number, blob: Blob) => {
    const form = new FormData()
    form.append('file', blob, 'answer.webm')
    const res = await fetch(`${BASE_URL}/api/interviews/${interviewId}/respond/audio`, {
      method: 'POST',
      headers: authHeaders(),
      body: form,
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json() as Promise<AudioRespondResult>
  },
}
