import { apiRequest } from './client'
import type { Job } from '../types/job'

export function listRenderJobs(projectId: number): Promise<Job[]> {
  return apiRequest(`/api/projects/${projectId}/render-jobs`)
}
