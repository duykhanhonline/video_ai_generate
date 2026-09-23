import { apiRequest } from './client'
import type { ActivityIdeas, Project, ProjectInput, ProjectReviewSummary } from '../types/project'
import type { Clip } from '../types/clip'
import type { ProjectCompletedVideo } from '../types/completedVideo'

export function listProjects(): Promise<Project[]> {
  return apiRequest('/api/projects')
}

export function getProjectReviewSummary(): Promise<ProjectReviewSummary[]> {
  return apiRequest('/api/projects/review-summary')
}

export function getProject(id: number): Promise<Project> {
  return apiRequest(`/api/projects/${id}`)
}

export function createProject(input: ProjectInput): Promise<Project> {
  return apiRequest('/api/projects', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function generateActivities(projectId: number, count: number): Promise<ActivityIdeas> {
  return apiRequest(`/api/projects/${projectId}/activities/generate`, {
    method: 'POST',
    body: JSON.stringify({ count }),
  })
}

export function listClips(projectId: number): Promise<Clip[]> {
  return apiRequest(`/api/projects/${projectId}/clips`)
}

export function createClips(projectId: number, activities: string[]): Promise<Clip[]> {
  return apiRequest(`/api/projects/${projectId}/clips`, {
    method: 'POST',
    body: JSON.stringify({ activities }),
  })
}

export function listProjectCompletedVideos(projectId: number): Promise<ProjectCompletedVideo[]> {
  return apiRequest(`/api/projects/${projectId}/completed-videos`)
}
