export interface Job {
  id: number
  project_id: number
  clip_id: number | null
  job_type: string
  provider: string
  external_job_id: string | null
  status: string
  progress: number
  error_message: string | null
  retry_count: number
  created_at: string
  started_at: string | null
  completed_at: string | null
}
