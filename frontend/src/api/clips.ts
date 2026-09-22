import { apiRequest, apiUpload } from './client'
import type { Clip } from '../types/clip'
import type { Job } from '../types/job'

export function generateImagePrompt(clipId: number): Promise<Clip> {
  return apiRequest(`/api/clips/${clipId}/image-prompt/generate`, { method: 'POST' })
}

export function generateClipImage(clipId: number, force = false): Promise<Job> {
  return apiRequest(`/api/clips/${clipId}/image/generate`, {
    method: 'POST',
    body: JSON.stringify({ force }),
  })
}

export function generateVideoPrompt(clipId: number): Promise<Clip> {
  return apiRequest(`/api/clips/${clipId}/video-prompt/generate`, { method: 'POST' })
}

export function uploadClipVideo(clipId: number, file: File): Promise<Clip> {
  const formData = new FormData()
  formData.append('file', file)
  return apiUpload(`/api/clips/${clipId}/video/upload`, formData)
}

export function updateClip(clipId: number, approved: boolean): Promise<Clip> {
  return apiRequest(`/api/clips/${clipId}`, {
    method: 'PATCH',
    body: JSON.stringify({ approved }),
  })
}
