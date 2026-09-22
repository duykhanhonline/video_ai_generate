export type ImageRatio = '1024x1024' | '1536x1024' | '1024x1536'

export interface Clip {
  id: number
  project_id: number
  activity: string
  status: string
  approved: boolean
  image_prompt: string | null
  image_ratio: ImageRatio
  reference_image_path: string | null
  image_asset_id: number | null
  video_prompt: string | null
  video_asset_id: number | null
  created_at: string
  updated_at: string
}
