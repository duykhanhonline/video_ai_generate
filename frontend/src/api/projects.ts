import { apiRequest } from './client'
import type { ActivityIdeas, Project, ProjectInput } from '../types/project'
import type { Clip } from '../types/clip'

export function listProjects(): Promise<Project[]> {
  return apiRequest('/api/projects')
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
