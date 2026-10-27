export interface Job {
  id: number
  title: string
  description: string
  required_skills: string[]
  preferred_skills: string[]
  rounds: string[]
}

export interface Skill {
  name: string
  claim_level: string | null
  evidence_count: number
}

export interface ResumeProfile {
  name: string | null
  skills: Skill[]
  projects: { title: string; description: string; skills_used: string[] }[]
  experience: { role: string; org: string; duration: string; summary: string }[]
  education: { degree: string; institution: string }[]
}

export interface Candidate {
  id: number
  job_id: number
  name: string | null
  resume_profile: ResumeProfile | null
  match_score: number | null
}

export interface InterviewSummary {
  id: number
  status: 'in_progress' | 'complete'
  rounds: string[]
}

export interface MyApplication extends Candidate {
  job_title: string
}

export interface StartInterviewResponse {
  interview_id: number
  round: string
  question: string
}

export interface RespondResult {
  type: 'follow_up' | 'next_question' | 'next_round' | 'interview_complete'
  question?: string
  round?: string
  report?: Report
}

export interface AudioMetrics {
  duration_sec: number
  mean_pitch_hz: number | null
  pitch_variation_hz: number | null
  mean_energy: number | null
  energy_variation: number | null
  silence_ratio: number
  speech_rate_wpm: number | null
  filler_count: number
  filler_density: number | null
  fillers_per_minute: number | null
}

export interface VideoMetrics {
  frames_sampled: number
  face_presence_ratio: number | null
  mean_head_yaw_deg: number | null
  gaze_away_ratio: number | null
}

export interface AudioRespondResult extends RespondResult {
  transcript: string
  audio_metrics: AudioMetrics | null
  video_metrics: VideoMetrics | null
}

export interface ScoreFusion {
  final_score: number | null
  components: {
    resume: number | null
    technical: number | null
    communication: number | null
    behavioral: number | null
    role_fit: number | null
  }
  communication_confidence: number
}

export interface Report {
  overall_recommendation: 'strong_candidate' | 'moderate_candidate' | 'weak_candidate'
  positive_evidence: string[]
  observed_limitations: string[]
  confidence: number
  fusion?: ScoreFusion
  candidate_name?: string | null
  job_title?: string
}
