export interface CompletedVideo {
  id: number
  clip_id: number
  asset_id: number
  file_path: string
  mime_type: string
  created_at: string
}

export interface ProjectCompletedVideo extends CompletedVideo {
  clip_activity: string
}
