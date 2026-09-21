import { apiRequest } from './client'
import type { Job } from '../types/job'

export function getJob(jobId: number): Promise<Job> {
  return apiRequest(`/api/jobs/${jobId}`)
}
