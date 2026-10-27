import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../lib/api'
import type { AudioMetrics, Report, VideoMetrics } from '../lib/types'
import { useVoiceRecorder } from '../lib/useVoiceRecorder'
import { Badge, Button, Panel, Textarea } from '../components/ui'

type Turn = {
  round: string
  question: string
  answer?: string
  isFollowUp: boolean
  audioMetrics?: AudioMetrics | null
  videoMetrics?: VideoMetrics | null
}

type Step = 'consent' | 'device_check' | 'interview' | 'done'

function ConsentStep({ onContinue }: { onContinue: () => void }) {
  const [agreed, setAgreed] = useState(false)

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Before you begin</h1>
        <p className="mt-2 max-w-lg text-sm text-ink-soft dark:text-ink-soft-dark">
          This interview is conducted by an AI system and reviewed by a human recruiter before any decision is made.
        </p>
      </div>

      <Panel className="space-y-3 p-5 text-sm">
        <p className="font-medium">What's recorded and analyzed</p>
        <ul className="list-disc space-y-1.5 pl-5 text-ink-soft dark:text-ink-soft-dark">
          <li>The content of your answers (typed or transcribed from your voice)</li>
          <li>If you record audio: speech characteristics like pace and pauses</li>
          <li>If you choose to enable it: basic webcam signals like whether a face is visible on camera</li>
        </ul>
        <p className="font-medium">What this system does not do</p>
        <ul className="list-disc space-y-1.5 pl-5 text-ink-soft dark:text-ink-soft-dark">
          <li>It does not detect lies, read emotions, or assess your mental state</li>
          <li>It does not use your accent, voice, or appearance to judge competence</li>
          <li>Webcam analysis is optional and off by default — you choose per answer</li>
        </ul>
      </Panel>

      <label className="flex items-start gap-2 text-sm">
        <input type="checkbox" className="mt-1" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} />
        <span>I understand what's being recorded and analyzed, and I consent to proceed.</span>
      </label>

      <Button onClick={onContinue} disabled={!agreed}>
        Continue
      </Button>
    </div>
  )
}

function DeviceCheckStep({ onContinue }: { onContinue: () => void }) {
  const [status, setStatus] = useState<'idle' | 'checking' | 'ok' | 'error'>('idle')

  async function testMic() {
    setStatus('checking')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach((t) => t.stop())
      setStatus('ok')
    } catch {
      setStatus('error')
    }
  }

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-semibold tracking-tight">Device check</h1>
      <p className="max-w-md text-sm text-ink-soft dark:text-ink-soft-dark">
        Check that your microphone works before starting. You can still type answers instead of recording at any
        point.
      </p>
      <Panel className="flex items-center gap-3 p-5">
        <Button variant="ghost" onClick={testMic} disabled={status === 'checking'}>
          {status === 'checking' ? 'Checking…' : 'Test microphone'}
        </Button>
        {status === 'ok' && <span className="text-sm text-good">Microphone detected.</span>}
        {status === 'error' && <span className="text-sm text-bad">Couldn't access a microphone.</span>}
      </Panel>
      <div className="flex gap-2">
        <Button onClick={onContinue}>{status === 'ok' ? 'Start interview' : 'Continue without testing'}</Button>
      </div>
    </div>
  )
}

export function InterviewPage() {
  const { candidateId } = useParams()
  const [step, setStep] = useState<Step>('consent')
  const [interviewId, setInterviewId] = useState<number | null>(null)
  const [turns, setTurns] = useState<Turn[]>([])
  const [answer, setAnswer] = useState('')
  const [busy, setBusy] = useState(false)
  const [webcamEnabled, setWebcamEnabled] = useState(false)
  const voice = useVoiceRecorder()

  async function start() {
    if (!candidateId) return
    setBusy(true)
    try {
      const res = await api.startInterview(Number(candidateId))
      setInterviewId(res.interview_id)
      setTurns([{ round: res.round, question: res.question, isFollowUp: false }])
      setStep('interview')
    } finally {
      setBusy(false)
    }
  }

  function applyResult(
    submittedAnswer: string,
    result: { type: string; question?: string; round?: string; report?: Report },
    audioMetrics?: AudioMetrics | null,
    videoMetrics?: VideoMetrics | null,
  ) {
    const current = turns[turns.length - 1]
    setTurns((t) => [...t.slice(0, -1), { ...current, answer: submittedAnswer, audioMetrics, videoMetrics }])

    if (result.type === 'interview_complete') {
      setStep('done')
    } else if (result.question) {
      const round = result.round ?? current.round
      setTurns((t) => [...t, { round, question: result.question!, isFollowUp: result.type === 'follow_up' }])
    }
  }

  async function submit() {
    if (!interviewId || !answer.trim()) return
    setBusy(true)
    const submittedAnswer = answer
    setAnswer('')
    try {
      const result = await api.respond(interviewId, submittedAnswer)
      applyResult(submittedAnswer, result)
    } finally {
      setBusy(false)
    }
  }

  async function submitVoice() {
    if (!interviewId) return
    const blob = await voice.stop()
    setBusy(true)
    try {
      const result = await api.respondAudio(interviewId, blob)
      applyResult(result.transcript, result, result.audio_metrics, result.video_metrics)
    } finally {
      setBusy(false)
    }
  }

  if (step === 'consent') {
    return <ConsentStep onContinue={() => setStep('device_check')} />
  }

  if (step === 'device_check') {
    return <DeviceCheckStep onContinue={start} />
  }

  if (step === 'done') {
    return (
      <div className="space-y-4">
        <h1 className="text-xl font-semibold tracking-tight">Thank you</h1>
        <p className="max-w-md text-sm text-ink-soft dark:text-ink-soft-dark">
          Your interview is complete. Your responses have been recorded and will be reviewed by the recruiting
          team alongside a human recruiter's judgment — this system does not make the final decision.
        </p>
        <Link to="/apply">
          <Button variant="ghost">Done</Button>
        </Link>
      </div>
    )
  }

  const current = turns[turns.length - 1]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight">Interview</h1>
        <Badge>{current.round}</Badge>
      </div>

      <div className="space-y-4">
        {turns.slice(0, -1).map((t, i) => (
          <Panel key={i} className="p-5 opacity-60">
            <p className="text-sm font-medium">{t.question}</p>
            <p className="mt-2 text-sm text-ink-soft dark:text-ink-soft-dark">{t.answer}</p>
            {t.audioMetrics && (
              <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 font-mono text-[11px] text-ink-soft dark:text-ink-soft-dark">
                <span>{t.audioMetrics.speech_rate_wpm ?? '—'} wpm</span>
                <span>{t.audioMetrics.filler_count} fillers</span>
                <span>{Math.round(t.audioMetrics.silence_ratio * 100)}% silence</span>
                {t.audioMetrics.pitch_variation_hz !== null && (
                  <span>±{t.audioMetrics.pitch_variation_hz}Hz pitch variation</span>
                )}
              </div>
            )}
            {t.videoMetrics && t.videoMetrics.face_presence_ratio !== null && (
              <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 font-mono text-[11px] text-ink-soft dark:text-ink-soft-dark">
                <span>{Math.round(t.videoMetrics.face_presence_ratio * 100)}% face presence</span>
                {t.videoMetrics.gaze_away_ratio !== null && (
                  <span>{Math.round(t.videoMetrics.gaze_away_ratio * 100)}% gaze away from camera</span>
                )}
              </div>
            )}
          </Panel>
        ))}

        <Panel className="p-5">
          {current.isFollowUp && (
            <span className="mb-2 inline-block font-mono text-xs text-accent">follow-up</span>
          )}
          <p className="text-sm font-medium">{current.question}</p>
          <Textarea
            className="mt-3"
            rows={5}
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer, or record it below…"
            disabled={busy || voice.recording}
          />
          {voice.error && <p className="mt-2 text-xs text-bad">{voice.error}</p>}
          <div className="mt-3 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                onClick={voice.recording ? submitVoice : () => voice.start(webcamEnabled)}
                disabled={busy}
                className={voice.recording ? 'border-bad text-bad' : ''}
              >
                <span className={`mr-2 inline-block size-2 rounded-full ${voice.recording ? 'animate-pulse bg-bad' : 'bg-ink-soft dark:bg-ink-soft-dark'}`} />
                {voice.recording ? 'Stop & submit' : 'Record answer'}
              </Button>
              <label className="flex items-center gap-1.5 text-xs text-ink-soft dark:text-ink-soft-dark">
                <input
                  type="checkbox"
                  checked={webcamEnabled}
                  onChange={(e) => setWebcamEnabled(e.target.checked)}
                  disabled={voice.recording}
                />
                Also analyze webcam (optional)
              </label>
            </div>
            <Button onClick={submit} disabled={busy || voice.recording || !answer.trim()}>
              {busy ? 'Evaluating…' : 'Submit answer'}
            </Button>
          </div>
        </Panel>
      </div>
    </div>
  )
}
