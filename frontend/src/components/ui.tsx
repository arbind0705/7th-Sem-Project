import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from 'react'

export function Panel({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={`rounded-md border border-line bg-paper-raised dark:border-line-dark dark:bg-paper-raised-dark ${className}`}
    >
      {children}
    </div>
  )
}

export function Button({
  variant = 'primary',
  className = '',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'ghost' }) {
  const base = 'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed'
  const styles =
    variant === 'primary'
      ? 'bg-accent text-white hover:bg-accent-strong'
      : 'border border-line text-ink hover:border-accent hover:text-accent dark:border-line-dark dark:text-ink-dark'
  return <button className={`${base} ${styles} ${className}`} {...props} />
}

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={`w-full rounded-md border border-line bg-paper px-3 py-2 text-sm text-ink outline-none transition-colors focus:border-accent dark:border-line-dark dark:bg-paper-dark dark:text-ink-dark ${props.className ?? ''}`}
    />
  )
}

export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      {...props}
      className={`w-full rounded-md border border-line bg-paper px-3 py-2 text-sm text-ink outline-none transition-colors focus:border-accent dark:border-line-dark dark:bg-paper-dark dark:text-ink-dark ${props.className ?? ''}`}
    />
  )
}

export function Label({ children }: { children: ReactNode }) {
  return <label className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-ink-soft dark:text-ink-soft-dark">{children}</label>
}

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div>
      <Label>{label}</Label>
      {children}
    </div>
  )
}

export function Badge({ tone = 'neutral', children }: { tone?: 'neutral' | 'good' | 'warn' | 'bad'; children: ReactNode }) {
  const tones: Record<string, string> = {
    neutral: 'bg-paper text-ink-soft border-line dark:bg-paper-dark dark:text-ink-soft-dark dark:border-line-dark',
    good: 'bg-[color-mix(in_oklab,var(--color-good)_14%,transparent)] text-good border-good/30',
    warn: 'bg-[color-mix(in_oklab,var(--color-warn)_14%,transparent)] text-warn border-warn/30',
    bad: 'bg-[color-mix(in_oklab,var(--color-bad)_14%,transparent)] text-bad border-bad/30',
  }
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 font-mono text-xs ${tones[tone]}`}>
      {children}
    </span>
  )
}
