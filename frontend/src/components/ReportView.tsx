import { useState } from 'react'
import type { Report } from '../lib/types'
import { Badge, Button, Panel } from './ui'

const recommendationTone: Record<Report['overall_recommendation'], 'good' | 'warn' | 'bad'> = {
  strong_candidate: 'good',
  moderate_candidate: 'warn',
  weak_candidate: 'bad',
}

export function ReportView({ report }: { report: Report }) {
  const [decision, setDecision] = useState<'accept' | 'review' | 'override' | null>(null)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">
          {report.candidate_name ?? 'Candidate'} — Assessment
        </h1>
        {report.job_title && (
          <p className="mt-0.5 text-sm text-ink-soft dark:text-ink-soft-dark">{report.job_title}</p>
        )}
        <div className="mt-2">
          <Badge tone={recommendationTone[report.overall_recommendation]}>
            {report.overall_recommendation.replace('_', ' ')}
          </Badge>
          <span className="ml-2 font-mono text-xs text-ink-soft dark:text-ink-soft-dark">
            confidence {report.confidence.toFixed(2)}
          </span>
        </div>
      </div>

      {report.fusion && (
        <Panel className="p-5">
          <div className="flex items-baseline justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-soft dark:text-ink-soft-dark">
              Score breakdown
            </h2>
            {report.fusion.final_score !== null && (
              <span className="font-mono text-sm">{Math.round(report.fusion.final_score * 100)}</span>
            )}
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-5">
            {Object.entries(report.fusion.components).map(([key, value]) => (
              <div key={key}>
                <p className="text-[11px] uppercase tracking-wide text-ink-soft dark:text-ink-soft-dark">
                  {key.replace('_', ' ')}
                </p>
                <p className="font-mono text-sm">{value !== null ? Math.round(value * 100) : '—'}</p>
              </div>
            ))}
          </div>
          <p className="mt-3 text-xs text-ink-soft dark:text-ink-soft-dark">
            Communication confidence {report.fusion.communication_confidence.toFixed(2)} — reflects how many
            answers had voice evidence to draw on.
          </p>
        </Panel>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <Panel className="p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-good">Positive evidence</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {report.positive_evidence.map((e, i) => (
              <li key={i} className="text-ink-soft dark:text-ink-soft-dark">
                {e}
              </li>
            ))}
          </ul>
        </Panel>
        <Panel className="p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-warn">Observed limitations</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {report.observed_limitations.length === 0 && (
              <li className="text-ink-soft dark:text-ink-soft-dark">None noted.</li>
            )}
            {report.observed_limitations.map((e, i) => (
              <li key={i} className="text-ink-soft dark:text-ink-soft-dark">
                {e}
              </li>
            ))}
          </ul>
        </Panel>
      </div>

      <Panel className="p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-soft dark:text-ink-soft-dark">
          Human review
        </h2>
        <p className="mt-1 text-xs text-ink-soft dark:text-ink-soft-dark">
          This is AI-assisted decision support, not an automated hiring decision — a recruiter makes the final call.
        </p>
        <div className="mt-4 flex gap-2">
          <Button variant={decision === 'accept' ? 'primary' : 'ghost'} onClick={() => setDecision('accept')}>
            Accept
          </Button>
          <Button variant={decision === 'review' ? 'primary' : 'ghost'} onClick={() => setDecision('review')}>
            Review further
          </Button>
          <Button variant={decision === 'override' ? 'primary' : 'ghost'} onClick={() => setDecision('override')}>
            Override
          </Button>
        </div>
      </Panel>
    </div>
  )
}
