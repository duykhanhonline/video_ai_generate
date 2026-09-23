import { apiRequest, apiUpload } from './client'
import type { Clip, ImageRatio } from '../types/clip'
import type { Job } from '../types/job'
import type { Asset } from '../types/asset'
import type { RenderManifest } from '../types/renderManifest'
import type { CompletedVideo } from '../types/completedVideo'

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

export function updateClipImagePrompt(clipId: number, imagePrompt: string): Promise<Clip> {
  return apiRequest(`/api/clips/${clipId}`, {
    method: 'PATCH',
    body: JSON.stringify({ image_prompt: imagePrompt }),
  })
}

export function updateClipImageRatio(clipId: number, imageRatio: ImageRatio): Promise<Clip> {
  return apiRequest(`/api/clips/${clipId}`, {
    method: 'PATCH',
    body: JSON.stringify({ image_ratio: imageRatio }),
  })
}

export function updateClipReferenceImage(clipId: number, referenceImagePath: string): Promise<Clip> {
  return apiRequest(`/api/clips/${clipId}`, {
    method: 'PATCH',
    body: JSON.stringify({ reference_image_path: referenceImagePath || null }),
  })
}

export function listClipImages(clipId: number): Promise<Asset[]> {
  return apiRequest(`/api/clips/${clipId}/images`)
}

export function selectClipImage(clipId: number, assetId: number): Promise<Clip> {
  return apiRequest(`/api/clips/${clipId}`, {
    method: 'PATCH',
    body: JSON.stringify({ image_asset_id: assetId }),
  })
}

export function deleteClip(clipId: number): Promise<void> {
  return apiRequest(`/api/clips/${clipId}`, { method: 'DELETE' })
}

export function exportClipManifest(clipId: number): Promise<RenderManifest> {
  return apiRequest(`/api/clips/${clipId}/render-manifest`)
}

export function uploadCompletedVideo(clipId: number, file: File): Promise<CompletedVideo> {
  const formData = new FormData()
  formData.append('file', file)
  return apiUpload(`/api/clips/${clipId}/completed-videos/upload`, formData)
}

export function listCompletedVideos(clipId: number): Promise<CompletedVideo[]> {
  return apiRequest(`/api/clips/${clipId}/completed-videos`)
}

export function deleteCompletedVideo(completedVideoId: number): Promise<void> {
  return apiRequest(`/api/clips/completed-videos/${completedVideoId}`, { method: 'DELETE' })
}
