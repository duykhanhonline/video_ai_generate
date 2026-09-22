export interface Project {
  id: number
  master_theme_id: number
  name: string
  status: string
  clip_count: number
  music_count: number
  target_duration: number
  image_provider: string
  video_provider: string
  music_provider: string
  created_at: string
  updated_at: string
}

export interface ProjectInput {
  master_theme_id: number
  name: string
  clip_count?: number
  music_count?: number
  target_duration: number
}

export interface ActivityIdeas {
  activities: string[]
}
