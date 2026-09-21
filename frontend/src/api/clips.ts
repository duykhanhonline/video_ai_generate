import { apiRequest } from './client'
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
