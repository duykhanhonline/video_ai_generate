import { apiRequest, apiUpload } from './client'
import type { MusicTrack } from '../types/musicTrack'

export function listProjectMusic(projectId: number): Promise<MusicTrack[]> {
  return apiRequest(`/api/projects/${projectId}/music`)
}

export function uploadMusicTrack(projectId: number, file: File, title: string): Promise<MusicTrack> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('title', title)
  return apiUpload(`/api/projects/${projectId}/music/upload`, formData)
}

export function deleteMusicTrack(trackId: number): Promise<void> {
  return apiRequest(`/api/music/${trackId}`, { method: 'DELETE' })
}

export function updateMusicTrack(trackId: number, approved: boolean): Promise<MusicTrack> {
  return apiRequest(`/api/music/${trackId}`, {
    method: 'PATCH',
    body: JSON.stringify({ approved }),
  })
}
