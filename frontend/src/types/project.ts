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
  owner_id: number | null
  category_id: number | null
  created_at: string
  updated_at: string
}

export interface ProjectInput {
  master_theme_id: number
  name: string
  clip_count?: number
  music_count?: number
  target_duration: number
  category_id?: number | null
}

export interface ActivityIdeas {
  activities: string[]
}

export interface ProjectReviewSummary {
  project_id: number
  project_name: string
  category_name: string | null
  completed_video_count: number
}
