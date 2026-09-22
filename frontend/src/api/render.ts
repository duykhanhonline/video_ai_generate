import { apiRequest } from './client'
import type { RenderManifest } from '../types/renderManifest'
import type { Job } from '../types/job'

export function exportRenderManifest(projectId: number): Promise<RenderManifest> {
  return apiRequest(`/api/projects/${projectId}/render-manifest`)
}

export function listRenderJobs(projectId: number): Promise<Job[]> {
  return apiRequest(`/api/projects/${projectId}/render-jobs`)
}
